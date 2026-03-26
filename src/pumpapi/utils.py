from __future__ import annotations

import base64
import time
from typing import Any, Dict, Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey


def lamports_to_sol(lamports: int) -> float:
    return lamports / 1_000_000_000


def sol_to_lamports(sol: float) -> int:
    return int(sol * 1_000_000_000)


def tokens_to_smallest_unit(tokens: float, decimals: int) -> int:
    return int(tokens * (10**decimals))


def smallest_unit_to_tokens(amount: int, decimals: int) -> float:
    return amount / (10**decimals)


def decode_base58(private_key_b58: str) -> bytes:
    return base64.b58decode(private_key_b58)


def encode_base58(data: bytes) -> str:
    return base64.b58encode(data).decode()


def parse_wallet_private_key(private_key: str) -> Keypair:
    decoded = decode_base58(private_key)
    return Keypair.from_bytes(decoded)


def calculate_slippage(amount: int, bps: int) -> int:
    return int(amount * bps / 10000)


def calculate_min_received(
    token_amount: int,
    token_decimals: int,
    sol_reserves: int,
    token_reserves: int,
    slippage_bps: int,
) -> int:
    if token_reserves == 0:
        return 0
    price = sol_reserves / token_reserves
    expected_sol = token_amount * price
    slippage_factor = 1 - (slippage_bps / 10000)
    min_expected = expected_sol * slippage_factor
    return int(min_expected * 1_000_000_000)


def format_timestamp(ts: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))


def format_market_cap(sol: float) -> str:
    if sol >= 1_000_000:
        return f"{sol / 1_000_000:.2f}M SOL"
    elif sol >= 1_000:
        return f"{sol / 1_000:.2f}K SOL"
    return f"{sol:.4f} SOL"


def validate_mint_address(mint: str) -> bool:
    try:
        Pubkey.from_string(mint)
        return True
    except Exception:
        return False


def build_transaction_config(
    slippage_bps: int = 100,
    priority_fee: int = 0,
) -> Dict[str, Any]:
    return {
        "slippage": slippage_bps,
        "priorityFee": priority_fee,
        "pool": "pump",
    }
