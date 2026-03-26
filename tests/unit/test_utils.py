import pytest
from pumpapi import (
    lamports_to_sol,
    sol_to_lamports,
    tokens_to_smallest_unit,
    smallest_unit_to_tokens,
    calculate_slippage,
    format_market_cap,
    validate_mint_address,
)


class TestUtilityFunctions:
    def test_lamports_to_sol(self):
        assert lamports_to_sol(1_000_000_000) == 1.0
        assert lamports_to_sol(500_000_000) == 0.5
        assert lamports_to_sol(0) == 0.0

    def test_sol_to_lamports(self):
        assert sol_to_lamports(1.0) == 1_000_000_000
        assert sol_to_lamports(0.5) == 500_000_000
        assert sol_to_lamports(0.0) == 0

    def test_tokens_to_smallest_unit(self):
        assert tokens_to_smallest_unit(1.0, 6) == 1_000_000
        assert tokens_to_smallest_unit(0.5, 6) == 500_000
        assert tokens_to_smallest_unit(1.0, 9) == 1_000_000_000

    def test_smallest_unit_to_tokens(self):
        assert smallest_unit_to_tokens(1_000_000, 6) == 1.0
        assert smallest_unit_to_tokens(500_000, 6) == 0.5
        assert smallest_unit_to_tokens(1_000_000_000, 9) == 1.0

    def test_calculate_slippage(self):
        assert calculate_slippage(1000, 100) == 10
        assert calculate_slippage(1000, 50) == 5
        assert calculate_slippage(1000, 0) == 0

    def test_format_market_cap(self):
        assert "M SOL" in format_market_cap(1_500_000)
        assert "K SOL" in format_market_cap(5_000)
        assert "SOL" in format_market_cap(500)

    def test_validate_mint_address_valid(self):
        assert validate_mint_address("EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD") is True

    def test_validate_mint_address_invalid(self):
        assert validate_mint_address("invalid") is False
        assert validate_mint_address("") is False
