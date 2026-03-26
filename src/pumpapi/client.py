from __future__ import annotations

import os
import json
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

import httpx
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from .types import (
    PumpApiConfig,
    TokenInfo,
    TradeInfo,
    MarketCapInfo,
    BondingCurveState,
    TokenMetadata,
    BuyRequest,
    SellRequest,
    TradeResult,
)
from .utils import (
    sol_to_lamports,
    tokens_to_smallest_unit,
    build_transaction_config,
    parse_wallet_private_key,
)


load_dotenv()


class PumpApiClient:
    BASE_URL = "https://pumpportal.fun/api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        wallet_private_key: Optional[str] = None,
        config: Optional[PumpApiConfig] = None,
    ):
        if config:
            self.config = config
        else:
            self.config = PumpApiConfig(
                api_key=api_key or os.getenv("PUMPAPI_API_KEY"),
                rpc_url=rpc_url or os.getenv("PUMPAPI_RPC_URL", "https://api.mainnet-beta.solana.com"),
            )

        self._client = httpx.Client(timeout=self.config.timeout)
        self._wallet: Optional[Keypair] = None

        if wallet_private_key:
            self._wallet = parse_wallet_private_key(wallet_private_key)
        elif os.getenv("PUMPAPI_WALLET_PRIVATE_KEY"):
            self._wallet = parse_wallet_private_key(os.getenv("PUMPAPI_WALLET_PRIVATE_KEY"))

        self._headers = {}
        if self.config.api_key:
            self._headers["Authorization"] = f"Bearer {self.config.api_key}"

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(self.config.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self._headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(2**attempt)
            except httpx.RequestError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(2**attempt)
        return {}

    def get_token(self, mint: str) -> TokenInfo:
        data = self._request("GET", f"/tokens/{mint}")
        return TokenInfo(**data)

    def get_token_by_ticker(self, ticker: str) -> TokenInfo:
        data = self._request("GET", f"/ticker/{ticker}")
        return TokenInfo(**data)

    def get_recent_tokens(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TokenMetadata]:
        params = {"limit": limit, "offset": offset}
        data = self._request("GET", "/tokens", params=params)
        return [TokenMetadata(**token) for token in data]

    def get_bonding_curve(self, mint: str) -> BondingCurveState:
        data = self._request("GET", f"/bonding-curve/{mint}")
        return BondingCurveState(**data)

    def get_market_cap(self, mint: str) -> MarketCapInfo:
        data = self._request("GET", f"/marketcap/{mint}")
        return MarketCapInfo(**data)

    def get_token_price(self, mint: str) -> float:
        data = self._request("GET", f"/price/{mint}")
        return data.get("price", 0.0)

    def get_trades(
        self,
        mint: str,
        limit: int = 50,
    ) -> List[TradeInfo]:
        params = {"limit": limit}
        data = self._request("GET", f"/trades/{mint}", params=params)
        return [TradeInfo(**trade) for trade in data]

    def get_fees(self, mint: str) -> Dict[str, Any]:
        return self._request("GET", f"/fees/{mint}")

    def get_global_data(self) -> Dict[str, Any]:
        return self._request("GET", "/global")

    def create_buy_transaction(
        self,
        mint: str,
        sol_amount: float,
        slippage_bps: int = 100,
        priority_fee: int = 0,
    ) -> Dict[str, Any]:
        if not self._wallet:
            raise ValueError("Wallet private key required for transactions")

        data = {
            "owner": str(self._wallet.pubkey()),
            "mint": mint,
            "amount": sol_to_lamports(sol_amount),
            "slippage": slippage_bps,
            "priorityFee": priority_fee,
            "pool": "pump",
        }
        return self._request("POST", "/buy", data=data)

    def create_sell_transaction(
        self,
        mint: str,
        token_amount: float,
        decimals: int = 6,
        slippage_bps: int = 100,
        priority_fee: int = 0,
    ) -> Dict[str, Any]:
        if not self._wallet:
            raise ValueError("Wallet private key required for transactions")

        data = {
            "owner": str(self._wallet.pubkey()),
            "mint": mint,
            "amount": tokens_to_smallest_unit(token_amount, decimals),
            "slippage": slippage_bps,
            "priorityFee": priority_fee,
            "pool": "pump",
        }
        return self._request("POST", "/sell", data=data)

    def execute_buy(
        self,
        mint: str,
        sol_amount: float,
        slippage_bps: int = 100,
        priority_fee: int = 0,
    ) -> TradeResult:
        tx_data = self.create_buy_transaction(mint, sol_amount, slippage_bps, priority_fee)
        return self._sign_and_send(tx_data)

    def execute_sell(
        self,
        mint: str,
        token_amount: float,
        decimals: int = 6,
        slippage_bps: int = 100,
        priority_fee: int = 0,
    ) -> TradeResult:
        tx_data = self.create_sell_transaction(mint, token_amount, decimals, slippage_bps, priority_fee)
        return self._sign_and_send(tx_data)

    def _sign_and_send(self, tx_data: Dict[str, Any]) -> TradeResult:
        if not self._wallet:
            raise ValueError("Wallet required for signing")

        try:
            from solana.transaction import Transaction
            from solders.transaction import Transaction as SoldersTransaction
            import base58

            encoded_tx = tx_data.get("transaction", "")
            if isinstance(encoded_tx, str):
                decoded = base58.b58decode(encoded_tx)
            else:
                decoded = encoded_tx

            tx = SoldersTransaction.deserialize(decoded)
            tx.sign(self._wallet)

            serialized = tx.serialize()
            encoded = base58.b58encode(serialized).decode()

            result = self._request("POST", "/broadcast", data={"transaction": encoded})
            return TradeResult(
                tx_hash=result.get("txHash", ""),
                success=result.get("success", True),
                timestamp=int(time.time()),
            )
        except Exception as e:
            return TradeResult(
                tx_hash="",
                success=False,
                error=str(e),
                timestamp=int(time.time()),
            )

    @property
    def wallet_address(self) -> Optional[str]:
        if self._wallet:
            return str(self._wallet.pubkey())
        return None

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
