import pytest


@pytest.fixture
def mock_token_data():
    return {
        "mint": "EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
        "name": "Test Token",
        "symbol": "TEST",
        "decimals": 6,
    }


@pytest.fixture
def mock_trade_data():
    return {
        "mint": "EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
        "sol_amount": 1_000_000_000,
        "token_amount": 1_000_000,
        "is_buy": True,
        "user": "TestUser123",
        "timestamp": 1234567890,
        "tx_hash": "TestTx123",
    }


@pytest.fixture
def mock_market_cap_data():
    return {
        "mint": "EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
        "market_cap_sol": 10000.0,
        "fdv_sol": 15000.0,
        "liquidity_sol": 5000.0,
        "holder_count": 100,
        "timestamp": 1234567890,
    }
