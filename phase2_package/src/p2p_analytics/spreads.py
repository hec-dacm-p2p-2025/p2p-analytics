from typing import Literal, Sequence
import pandas as pd

from .io import load_binance_currency, load_binance_master

ByType = Literal["day", "hour"]


def _ensure_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Ensure `col` is in datetime64[ns] format."""
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        df = df.copy()
        df[col] = pd.to_datetime(df[col])
    return df


def _p2p_spread_core(df: pd.DataFrame, currency: str, by: ByType = "day") -> pd.DataFrame:
    """
    Core BUY–SELL spread computation on a DataFrame that already
    contains one fiat.
    """
    df_cur = df.copy()

    if by == "day":
        group_cols = ["date"]
    elif by == "hour":
        df_cur = _ensure_datetime(df_cur, "scrape_datetime")
        df_cur["hour"] = df_cur["scrape_datetime"].dt.hour
        group_cols = ["date", "hour"]
    else:
        raise ValueError("by must be 'day' or 'hour'.")

    grouped = (
        df_cur
        .groupby(group_cols + ["side"], as_index=False)["price"]
        .mean()
        .pivot_table(
            index=group_cols,
            columns="side",
            values="price"
        )
        .rename(columns={"BUY": "avg_buy_price", "SELL": "avg_sell_price"})
        .reset_index()
    )

    grouped["currency"] = currency

    # Spread metrics
    grouped["spread_abs"] = (grouped["avg_sell_price"] - grouped["avg_buy_price"]).abs()
    mid = (grouped["avg_sell_price"] + grouped["avg_buy_price"]) / 2
    grouped["spread_pct"] = grouped["spread_abs"] / mid * 100

    return grouped


def p2p_spread(
    currency: str,
    by: ByType = "day",
    root: str | None = None,
) -> pd.DataFrame:
    """
    Compute BUY–SELL spread for a given currency using the Phase 1 parquet files.

    Parameters
    ----------
    currency : str
        Fiat code, e.g. 'ARS', 'BOB', 'EUR'.
    by : {'day', 'hour'}, default 'day'
        Aggregation level for spreads.
    root : path-like, optional
        Root of processed data. If None, infer from project layout.

    Returns
    -------
    pandas.DataFrame
        Columns include:
        - date (and hour if by='hour')
        - currency
        - avg_buy_price
        - avg_sell_price
        - spread_abs
        - spread_pct
    """
    df = load_binance_currency(currency, root=root)
    return _p2p_spread_core(df, currency, by=by)


def intraday_profile(
    currency: str,
    root: str | None = None,
) -> pd.DataFrame:
    """
    Intraday price profile for a given currency (average over all days).

    Parameters
    ----------
    currency : str
        Fiat currency code.
    root : path-like, optional
        Root of processed data.

    Returns
    -------
    pandas.DataFrame
        One row per hour (0–23) with:
        - hour
        - currency
        - mean_buy_price
        - mean_sell_price
    """
    df = load_binance_currency(currency, root=root)
    df = _ensure_datetime(df, "scrape_datetime")
    df_cur = df.copy()
    df_cur["hour"] = df_cur["scrape_datetime"].dt.hour

    grouped = (
        df_cur
        .groupby(["hour", "side"], as_index=False)["price"]
        .mean()
        .pivot_table(
            index="hour",
            columns="side",
            values="price"
        )
        .rename(columns={"BUY": "mean_buy_price", "SELL": "mean_sell_price"})
        .reset_index()
    )

    grouped["currency"] = currency
    return grouped


def fiat_comparison(
    currencies: Sequence[str],
    root: str | None = None,
) -> pd.DataFrame:
    """
    Build a comparison table across multiple fiat currencies (daily metrics).

    Parameters
    ----------
    currencies : sequence of str
        List of fiat codes to include (e.g. ['ARS', 'BOB', 'EUR']).
    root : path-like, optional
        Root of processed data.

    Returns
    -------
    pandas.DataFrame
        One row per date per currency, with:
        - date
        - currency
        - avg_buy_price
        - avg_sell_price
        - spread_abs
        - spread_pct
    """
    df = load_binance_master(root=root)
    df_sub = df[df["currency"].isin(currencies)].copy()

    grouped = (
        df_sub
        .groupby(["date", "currency", "side"], as_index=False)["price"]
        .mean()
        .pivot_table(
            index=["date", "currency"],
            columns="side",
            values="price"
        )
        .rename(columns={"BUY": "avg_buy_price", "SELL": "avg_sell_price"})
        .reset_index()
    )

    grouped["spread_abs"] = (grouped["avg_sell_price"] - grouped["avg_buy_price"]).abs()
    mid = (grouped["avg_sell_price"] + grouped["avg_buy_price"]) / 2
    grouped["spread_pct"] = grouped["spread_abs"] / mid * 100

    return grouped

