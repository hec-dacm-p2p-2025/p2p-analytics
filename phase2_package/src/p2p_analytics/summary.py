from __future__ import annotations

from typing import Literal, Sequence, Optional
import numpy as np
import pandas as pd

from .io import load_binance_currency, load_binance_master
from .spreads import _ensure_datetime 


ByType = Literal["day", "hour"]


def _prepare_time_grouping(df: pd.DataFrame, by: ByType) -> tuple[pd.DataFrame, list[str]]:
    """Add time grouping columns (day or hour) and return (df, group_cols)."""
    df = df.copy()
    if by == "day":
        group_cols = ["date", "currency"]
    elif by == "hour":
        df = _ensure_datetime(df, "scrape_datetime")
        df["hour"] = df["scrape_datetime"].dt.hour
        group_cols = ["date", "hour", "currency"]
    else:
        raise ValueError("by must be 'day' or 'hour'.")
    return df, group_cols


def p2p_summary(
    currency: Optional[str] = None,
    currencies: Optional[Sequence[str]] = None,
    by: ByType = "day",
    root: str | None = None,
) -> pd.DataFrame:
    """
    Full P2P summary: prices, spreads, extremes, and changes vs previous period.

    If `currencies` is provided, uses the multi-currency master file.
    Otherwise, uses the per-currency historical file for `currency`.
    """
    if currencies is not None and currency is not None:
        raise ValueError("Use either `currency` OR `currencies`, not both.")

    if currencies is not None:
        df = load_binance_master(root=root)
        df = df[df["currency"].isin(currencies)].copy()
    elif currency is not None:
        df = load_binance_currency(currency, root=root)
    else:
        raise ValueError("You must provide either `currency` or `currencies`.")

    df, group_cols = _prepare_time_grouping(df, by)

    # Aggregate BUY and SELL separately for min/max/mean
    agg = (
        df.groupby(group_cols + ["side"])
        .agg(
            avg_price=("price", "mean"),
            min_price=("price", "min"),
            max_price=("price", "max"),
        )
        .reset_index()
    )

    # Pivot side to columns
    summary = (
        agg.pivot_table(
            index=group_cols,
            columns="side",
            values=["avg_price", "min_price", "max_price"],
        )
        .reset_index()
    )

    # Flatten MultiIndex columns: ('avg_price', 'BUY') -> 'avg_buy_price'
    summary.columns = [
        "_".join(col).strip("_").lower().replace(" ", "_")
        if isinstance(col, tuple)
        else col
        for col in summary.columns
    ]

    # Rename for clarity
    rename_map = {
        "avg_price_buy": "avg_buy_price",
        "avg_price_sell": "avg_sell_price",
        "min_price_buy": "min_buy_price",
        "min_price_sell": "min_sell_price",
        "max_price_buy": "max_buy_price",
        "max_price_sell": "max_sell_price",
    }
    summary = summary.rename(columns=rename_map)

    # Mid price and spreads
    summary["mid_price"] = (summary["avg_buy_price"] + summary["avg_sell_price"]) / 2
    summary["spread_abs"] = (summary["avg_sell_price"] - summary["avg_buy_price"]).abs()
    mid = summary["mid_price"]
    summary["spread_pct"] = summary["spread_abs"] / mid * 100

    # Changes vs previous period, per currency
    sort_cols = ["currency", "date"]
    if by == "hour":
        sort_cols.append("hour")

    summary = summary.sort_values(sort_cols).reset_index(drop=True)

    summary["mid_price_change"] = (
        summary.groupby("currency")["mid_price"].diff()
    )
    summary["mid_price_pct_change"] = (
        summary.groupby("currency")["mid_price"].pct_change() * 100
    )

    summary["spread_abs_change"] = (
        summary.groupby("currency")["spread_abs"].diff()
    )
    summary["spread_pct_change"] = (
        summary.groupby("currency")["spread_pct"].diff()
    )

    return summary


def top_advertisers(
    currency: str,
    side: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metric: Literal["volume", "ads"] = "volume",
    n: int = 10,
    root: str | None = None,
) -> pd.DataFrame:
    """
    Rank merchants by activity (ad count) and/or volume (sum of max_amount).

    Parameters
    ----------
    currency : str
        Fiat currency code.
    side : {'BUY', 'SELL'} or None
        Filter by side if provided.
    start_date, end_date : 'YYYY-MM-DD' or None
        Optional date range filter.
    metric : {'volume', 'ads'}
        Ranking metric: total volume (sum of max_amount) or number of ads.
    n : int
        Number of top merchants to return.
    """
    df = load_binance_currency(currency, root=root).copy()

    # Filter by side
    if side is not None:
        df = df[df["side"] == side]

    # Ensure date is datetime-like for filtering
    df["date"] = pd.to_datetime(df["date"]).dt.date

    if start_date is not None:
        start = pd.to_datetime(start_date).date()
        df = df[df["date"] >= start]

    if end_date is not None:
        end = pd.to_datetime(end_date).date()
        df = df[df["date"] <= end]

    if df.empty:
        return df.head(0)  # empty with same columns

    grouped = (
        df.groupby("merchant_name")
        .agg(
            ads_count=("run_index", "count"),
            total_volume=("max_amount", "sum"),
            avg_finish_rate=("finish_rate", "mean"),
            avg_positive_rate=("positive_rate", "mean"),
        )
        .reset_index()
    )

    if metric == "volume":
        sort_col = "total_volume"
    elif metric == "ads":
        sort_col = "ads_count"
    else:
        raise ValueError("metric must be 'volume' or 'ads'.")

    grouped = grouped.sort_values(sort_col, ascending=False).head(n)
    grouped["currency"] = currency
    if side is not None:
        grouped["side"] = side

    return grouped


def price_volatility(
    currency: str,
    by: Literal["day", "hour"] = "day",
    window: int = 7,
    root: str | None = None,
) -> pd.DataFrame:
    """
    Compute rolling volatility of the mid price over time.

    Volatility is defined as the rolling standard deviation of
    log-returns of the mid price over the given window size.
    """
    df = load_binance_currency(currency, root=root)
    df, group_cols = _prepare_time_grouping(df, by)

    # Daily / hourly mid price
    agg = (
        df.groupby(group_cols + ["side"], as_index=False)["price"]
        .mean()
        .pivot_table(
            index=group_cols,
            columns="side",
            values="price",
        )
        .rename(columns={"BUY": "avg_buy_price", "SELL": "avg_sell_price"})
        .reset_index()
    )

    agg["mid_price"] = (agg["avg_buy_price"] + agg["avg_sell_price"]) / 2

    # Sort for time order
    sort_cols = ["currency", "date"]
    if by == "hour":
        sort_cols.append("hour")

    agg = agg.sort_values(sort_cols).reset_index(drop=True)

    # Log-returns and rolling std
    agg["log_price"] = np.log(agg["mid_price"])
    agg["log_return"] = agg.groupby("currency")["log_price"].diff()

    agg["volatility"] = (
        agg.groupby("currency")["log_return"]
        .rolling(window=window)
        .std()
        .reset_index(level=0, drop=True)
    )

    return agg
