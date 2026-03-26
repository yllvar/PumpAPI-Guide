import pytest
from pumpapi_strategies import (
    TradingSignal,
    SignalType,
    SignalStrength,
    SignalBatch,
    Order,
    OrderStatus,
)
from datetime import datetime


class TestTradingSignal:
    def test_create_buy_signal(self):
        signal = TradingSignal(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal_type=SignalType.BUY,
            strength=0.8,
            price=0.001,
        )
        assert signal.is_buy() is True
        assert signal.is_sell() is False

    def test_create_sell_signal(self):
        signal = TradingSignal(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal_type=SignalType.SELL,
            strength=0.8,
            price=0.001,
        )
        assert signal.is_buy() is False
        assert signal.is_sell() is True

    def test_signal_strength_check(self):
        signal = TradingSignal(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal_type=SignalType.BUY,
            strength=0.8,
        )
        assert signal.is_strong(0.7) is True
        assert signal.is_strong(0.9) is False

    def test_signal_to_dict(self):
        signal = TradingSignal(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal_type=SignalType.BUY,
            strength=0.8,
            confidence=0.9,
            reason="Test reason",
        )
        d = signal.to_dict()
        assert d["mint"] == "EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD"
        assert d["type"] == "buy"
        assert d["strength"] == 0.8


class TestSignalBatch:
    def test_add_signals(self):
        batch = SignalBatch()
        
        signal1 = TradingSignal(
            mint="Mint1",
            signal_type=SignalType.BUY,
            strength=0.8,
        )
        signal2 = TradingSignal(
            mint="Mint2",
            signal_type=SignalType.SELL,
            strength=0.6,
        )
        
        batch.add(signal1)
        batch.add(signal2)
        
        assert len(batch.signals) == 2
        assert len(batch.buy_signals()) == 1
        assert len(batch.sell_signals()) == 1

    def test_strong_signals(self):
        batch = SignalBatch()
        
        signal1 = TradingSignal(
            mint="Mint1",
            signal_type=SignalType.BUY,
            strength=0.8,
        )
        signal2 = TradingSignal(
            mint="Mint2",
            signal_type=SignalType.BUY,
            strength=0.5,
        )
        
        batch.add(signal1)
        batch.add(signal2)
        
        strong = batch.strong_signals(0.7)
        assert len(strong) == 1
        assert strong[0].mint == "Mint1"


class TestOrder:
    def test_create_pending_order(self):
        signal = TradingSignal(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal_type=SignalType.BUY,
            strength=0.8,
        )
        
        order = Order(
            order_id="order_1",
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal=signal,
            amount=0.1,
            order_type=SignalType.BUY,
        )
        
        assert order.status == OrderStatus.PENDING
        assert order.order_id == "order_1"
        assert order.amount == 0.1

    def test_order_status_transitions(self):
        signal = TradingSignal(
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal_type=SignalType.BUY,
            strength=0.8,
        )
        
        order = Order(
            order_id="order_1",
            mint="EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD",
            signal=signal,
            amount=0.1,
            order_type=SignalType.BUY,
        )
        
        order.status = OrderStatus.SUBMITTED
        assert order.status == OrderStatus.SUBMITTED
        
        order.status = OrderStatus.FILLED
        order.tx_hash = "Tx123"
        assert order.status == OrderStatus.FILLED
        assert order.tx_hash == "Tx123"


class TestSignalStrength:
    def test_signal_strength_values(self):
        assert SignalStrength.WEAK.value == 0.25
        assert SignalStrength.LOW.value == 0.5
        assert SignalStrength.MEDIUM.value == 0.75
        assert SignalStrength.STRONG.value == 1.0
