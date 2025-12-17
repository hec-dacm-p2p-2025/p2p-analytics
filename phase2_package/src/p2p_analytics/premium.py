from typing import Literal
import pandas as pd

from .io import load_binance_currency, load_bcb_master
from .spreads import _p2p_spread_core


def official_premium(
    currency: str,
    by: Literal["day"] = "day",
    root: str | None = None,
) -> pd.DataFrame:
    """
    Compare P2P prices vs official BCB rate for a given currency.

    Parameters
    ----------
    currency : str
        Fiat currency code.
    by : {'day'}, default 'day'
        Aggregation level (currently only daily).
    root : path-like, optional
        Root of processed data from Phase 1.

    Returns
    -------
    pandas.DataFrame
        Columns:
        - date
        - currency
        - p2p_avg_price
        - official_exchange_rate
        - premium_abs
        - premium_pct
    """
    if by != "day":
        raise NotImplementedError("Only by='day' is implemented for now.")

    # 1) Binance daily mid-price
    df_binance = load_binance_currency(currency, root=root)
    daily = _p2p_spread_core(df_binance, currency, by="day")
    # mid-market price
    daily["p2p_avg_price"] = (daily["avg_buy_price"] + daily["avg_sell_price"]) / 2

    # 2) BCB official rate
    df_bcb = load_bcb_master(root=root)
    df_bcb_cur = df_bcb[df_bcb["currency"] == currency].copy()

    merged = daily.merge(
        df_bcb_cur[["date", "currency", "official_exchange_rate"]],
        on=["date", "currency"],
        how="inner",
    )

    merged["premium_abs"] = (merged["p2p_avg_price"] - merged["official_exchange_rate"]).abs()
    merged["premium_pct"] = (
        merged["p2p_avg_price"] / merged["official_exchange_rate"] - 1.0
    ) * 100

    return merged[[
        "date",
        "currency",
        "p2p_avg_price",
        "official_exchange_rate",
        "premium_abs",
        "premium_pct",
    ]]

