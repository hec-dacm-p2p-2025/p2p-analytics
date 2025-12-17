# Get started

This page shows how to perform the most common tasks with `p2p-analytics`.

## Define correct root path

Before loading any data, make sure to set the correct root path where the Phase 1 pipeline has stored the parquet datasets. Compute the following code in the phase 3 notebook:

```python
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

EXPORTS = SCRIPT_DIR / "exports"
EXPORTS.mkdir(parents=True, exist_ok=True)

PHASE1_ROOT = REPO_ROOT / "phase1_data_pipeline" / "data" / "processed"
MASTER = PHASE1_ROOT / "binance" / "p2p_master.parquet"
```

## Compute spread

```python
from p2p_analytics import p2p_spread

spread_ars = p2p_spread("ARS", by="day", root=PHASE1_ROOT)
```

## Intraday profile
```python
from p2p_analytics import intraday_profile

profile_ars = intraday_profile("ARS", start= '2025-12-09', end='2025-12-10' root=PHASE1_ROOT)
```

## Compare multiple currencies
```python
from p2p_analytics import fiat_comparison

fiats = fiat_comparison(["ARS", "BOB", "MXN"], root=PHASE1_ROOT)
```

## Premium vs. official exchange rate

```python
from p2p_analytics import official_premium

premium_ars = official_premium("ARS", root=PHASE1_ROOT)
```

## Volatility and summary statistics
```python
from p2p_analytics import p2p_summary, price_volatility

summary_ars = p2p_summary("ARS", root=PHASE1_ROOT)
vol_ars = price_volatility("ARS", window=7, root=PHASE1_ROOT)
```

## Outputs
All outputs are standard pandas DataFrame and can be exported directly to PowerBI:

```python
summary_ars.to_parquet("exports/summary_ARS.parquet") # exports in .parquet file

summary_ars.to_csv("exports/summary_ARS.csv") # exports in .csv file
```
