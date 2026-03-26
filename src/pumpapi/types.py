from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    mint: str
    name: str
    symbol: str
    decimals: int
    uri: Optional[str] = None


class TradeInfo(BaseModel):
    mint: str
    sol_amount: int
    token_amount: int
    is_buy: bool
    user: str
    timestamp: int
    tx_hash: str


class MarketCapInfo(BaseModel):
    mint: str
    market_cap_sol: float
    fdv_sol: float
    liquidity_sol: float
    holder_count: int
    timestamp: int


class BondingCurveState(BaseModel):
    mint: str
    virtual_token_reserves: int
    virtual_sol_reserves: int
    real_token_reserves: int
    real_sol_reserves: int
    token_supply: int
    initialized: bool
    complete: bool


class TokenMetadata(BaseModel):
    mint: str
    name: str
    symbol: str
    uri: str
    timestamp: int
    liquidity: float
    market_cap: float


class WebSocketMessage(BaseModel):
    method: str
    data: Optional[dict] = None
    subscription: Optional[str] = None


class BuyRequest(BaseModel):
    mint: str
    amount: int = Field(..., description="Amount in SOL (lamports)")
    slippage_bps: int = 100
    priority_fee: int = 0


class SellRequest(BaseModel):
    mint: str
    amount: int = Field(..., description="Amount in tokens (smallest unit)")
    slippage_bps: int = 100
    priority_fee: int = 0


class TradeResult(BaseModel):
    tx_hash: str
    success: bool
    error: Optional[str] = None
    timestamp: int


class StreamSubscription(BaseModel):
    type: str = Field(..., description="Event type: new_token, trade, market_cap, bonding_curve")
    mint: Optional[str] = None
    subscription_id: Optional[str] = None


class PumpApiConfig(BaseModel):
    api_key: Optional[str] = None
    rpc_url: str = "https://api.mainnet-beta.solana.com"
    wss_url: str = "wss://pumpportal.fun/api/data"
    slippage_bps: int = 100
    priority_fee_micro_lamports: int = 1000
    timeout: int = 30
    max_retries: int = 3
