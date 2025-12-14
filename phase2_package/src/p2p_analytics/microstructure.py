from typing import Literal
import pandas as pd

from .io import load_binance_currency
from .spreads import _ensure_datetime


def _order_imbalance_core(
    df: pd.DataFrame,
    currency: str,
    by: Literal["hour"] = "hour",
) -> pd.DataFrame:
    """
    Core order imbalance computation for one currency on a DataFrame.
    """
    if by != "hour":
        raise NotImplementedError("Only by='hour' is implemented for now.")

    df_cur = df.copy()
    df_cur = _ensure_datetime(df_cur, "scrape_datetime")
    df_cur["hour"] = df_cur["scrape_datetime"].dt.hour

    # Approximate volume with max_amount
    df_cur["volume"] = df_cur["max_amount"]

    grouped = (
        df_cur
        .groupby(["date", "hour", "side"], as_index=False)["volume"]
        .sum()
        .pivot_table(
            index=["date", "hour"],
            columns="side",
            values="volume",
            fill_value=0.0,
        )
        .rename(columns={"BUY": "buy_volume", "SELL": "sell_volume"})
        .reset_index()
    )

    grouped["currency"] = currency
    denom = grouped["buy_volume"] + grouped["sell_volume"]

    grouped["imbalance"] = 0.0
    nonzero = denom > 0
    grouped.loc[nonzero, "imbalance"] = (
        (grouped.loc[nonzero, "buy_volume"] - grouped.loc[nonzero, "sell_volume"])
        / denom[nonzero]
    )

    return grouped


def order_imbalance(
    currency: str,
    by: Literal["hour"] = "hour",
    root: str | None = None,
) -> pd.DataFrame:
    """
    Compute hourly order imbalance for a given currency using historical_fiat data.

    Parameters
    ----------
    currency : str
        Fiat currency code.
    by : {'hour'}, default 'hour'
        Aggregation level.
    root : path-like, optional
        Root of processed data from Phase 1.

    Returns
    -------
    pandas.DataFrame
        One row per (date, hour) with:
        - date
        - hour
        - currency
        - buy_volume
        - sell_volume
        - imbalance
    """
    df = load_binance_currency(currency, root=root)
    return _order_imbalance_core(df, currency, by=by)

