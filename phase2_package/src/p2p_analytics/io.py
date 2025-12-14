from __future__ import annotations
from pathlib import Path
from typing import Optional, Union
import datetime as dt

import pandas as pd

PathLike = Union[str, Path]


def get_processed_root(root: Optional[PathLike] = None) -> Path:
    """
    Return the root path to the Phase 1 processed data.

    If `root` is None, we assume the following project layout:

        final-project/
        ├─ phase1_data_pipeline/
        │   └─ data/processed/...
        └─ phase2_package/
            └─ src/p2p_analytics/io.py  (this file)

    so the processed root is:
        final-project/phase1_data_pipeline/data/processed
    """
    if root is not None:
        return Path(root)

    # This file: final-project/phase2_package/src/p2p_analytics/io.py
    here = Path(__file__).resolve()
    final_project_root = here.parents[3]  # go up: p2p_analytics -> src -> phase2_package -> final-project
    return final_project_root / "phase1_data_pipeline" / "data" / "processed"

# ---------------------------------------------------------------------
# BINANCE LOADERS
# ---------------------------------------------------------------------

def load_binance_currency(
    currency: str,
    root: Optional[PathLike] = None,
) -> pd.DataFrame:
    """
    Load historical Binance P2P data for a single fiat currency. It reads from: `<processed_root>/binance/historical_fiat/<CURRENCY>.parquet`
    """
    processed_root = get_processed_root(root)
    path = processed_root / "binance" / "historical_fiat" / f"{currency}.parquet"
    return pd.read_parquet(path)


def load_binance_master(root: Optional[PathLike] = None) -> pd.DataFrame:
    """
    Load the full Binance P2P history (all fiats, all time). It reads from: `<processed_root>/binance/p2p_master.parquet`
    """
    processed_root = get_processed_root(root)
    path = processed_root / "binance" / "p2p_master.parquet"
    return pd.read_parquet(path)

def load_binance_daily(
    date: Union[str, dt.date],
    root: Optional[PathLike] = None,
) -> pd.DataFrame:
    """
    Load one daily snapshot of Binance P2P data.

    Parameters
    ----------
    date : str or datetime.date Date of interest; if string, should be 'YYYY-MM-DD'. This function reads from: `<processed_root>/binance/daily_snapshots/daily_snapshot_<YYYY-MM-DD>.parquet`
    """
    if isinstance(date, dt.date):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)

    processed_root = get_processed_root(root)
    filename = f"daily_snapshot_{date_str}.parquet"
    path = processed_root / "binance" / "daily_snapshots" / filename
    return pd.read_parquet(path)


# ---------------------------------------------------------------------
# BCB LOADERS
# ---------------------------------------------------------------------

def load_bcb_master(root: Optional[PathLike] = None) -> pd.DataFrame:
    """
    Load the full BCB official-rate history.It reads from: `<processed_root>/bcb/bcb_master.parquet`
    """
    processed_root = get_processed_root(root)
    path = processed_root / "bcb" / "bcb_master.parquet"
    return pd.read_parquet(path)


def load_bcb_latest(root: Optional[PathLike] = None) -> pd.DataFrame:
    """
    Load the most recent BCB official rates (e.g. today's table). This function reads from: `<processed_root>/bcb/bcb_today.parquet`
    """
    processed_root = get_processed_root(root)
    path = processed_root / "bcb" / "bcb_today.parquet"
    return pd.read_parquet(path)



