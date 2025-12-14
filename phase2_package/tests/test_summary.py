import pytest
from p2p_analytics.summary import p2p_summary


def test_p2p_summary_output(sample_binance_df, monkeypatch):
    # Monkeypatch loader to return test df
    from p2p_analytics import summary
    monkeypatch.setattr(summary, "load_binance_currency", lambda c, root=None: sample_binance_df)

    result = p2p_summary(currency="ARS")

    assert "mid_price" in result.columns
    assert "spread_pct" in result.columns
    assert result["mid_price"].iloc[0] == pytest.approx((1500 + 1510) / 2)
