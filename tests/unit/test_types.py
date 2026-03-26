import pytest
from pumpapi.types import (
    TokenInfo,
    TradeInfo,
    MarketCapInfo,
    BondingCurveState,
    TokenMetadata,
    BuyRequest,
    SellRequest,
    TradeResult,
    PumpApiConfig,
)


class TestTokenInfo:
    def test_create_token_info(self):
        token = TokenInfo(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            name="USD Coin",
            symbol="USDC",
            decimals=6,
        )
        assert token.name == "USD Coin"
        assert token.symbol == "USDC"
        assert token.decimals == 6


class TestTradeInfo:
    def test_create_trade_info(self):
        trade = TradeInfo(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            sol_amount=1_000_000_000,
            token_amount=1_000_000,
            is_buy=True,
            user="User123",
            timestamp=1234567890,
            tx_hash="Tx123",
        )
        assert trade.is_buy is True
        assert trade.sol_amount == 1_000_000_000


class TestMarketCapInfo:
    def test_create_market_cap(self):
        mc = MarketCapInfo(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            market_cap_sol=10000.0,
            fdv_sol=15000.0,
            liquidity_sol=5000.0,
            holder_count=100,
            timestamp=1234567890,
        )
        assert mc.market_cap_sol == 10000.0
        assert mc.liquidity_sol == 5000.0


class TestBondingCurveState:
    def test_create_bonding_curve(self):
        curve = BondingCurveState(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            virtual_token_reserves=1_000_000_000,
            virtual_sol_reserves=500_000_000_000,
            real_token_reserves=0,
            real_sol_reserves=0,
            token_supply=1_000_000_000,
            initialized=True,
            complete=False,
        )
        assert curve.initialized is True
        assert curve.complete is False


class TestBuyRequest:
    def test_create_buy_request(self):
        req = BuyRequest(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            amount=1_000_000_000,
        )
        assert req.mint == "EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD"
        assert req.amount == 1_000_000_000
        assert req.slippage_bps == 100


class TestSellRequest:
    def test_create_sell_request(self):
        req = SellRequest(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            amount=1_000_000,
        )
        assert req.amount == 1_000_000


class TestTradeResult:
    def test_create_successful_trade(self):
        result = TradeResult(
            tx_hash="Tx123",
            success=True,
            timestamp=1234567890,
        )
        assert result.success is True

    def test_create_failed_trade(self):
        result = TradeResult(
            tx_hash="",
            success=False,
            error="Insufficient funds",
            timestamp=1234567890,
        )
        assert result.success is False
        assert result.error == "Insufficient funds"


class TestPumpApiConfig:
    def test_create_default_config(self):
        config = PumpApiConfig()
        assert config.rpc_url == "https://api.mainnet-beta.solana.com"
        assert config.slippage_bps == 100
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_create_custom_config(self):
        config = PumpApiConfig(
            api_key="test_key",
            slippage_bps=200,
            timeout=60,
        )
        assert config.api_key == "test_key"
        assert config.slippage_bps == 200
        assert config.timeout == 60
