import pytest
from p2p_analytics.spreads import _p2p_spread_core


def test_p2p_spread_core_daily(sample_binance_df):
    df = sample_binance_df
    result = _p2p_spread_core(df, currency="ARS", by="day")

    assert "avg_buy_price" in result.columns
    assert "avg_sell_price" in result.columns
    assert "spread_abs" in result.columns
    assert result.iloc[0]["spread_abs"] == pytest.approx(1510.0 - 1500.0)
