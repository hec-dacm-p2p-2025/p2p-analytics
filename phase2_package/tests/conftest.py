import pandas as pd
import pytest
from datetime import datetime


@pytest.fixture
def sample_binance_df():
    return pd.DataFrame({
        "scrape_datetime": [
            datetime(2025, 12, 7, 10, 0),
            datetime(2025, 12, 7, 11, 0),
        ],
        "date": ["2025-12-07", "2025-12-07"],
        "currency": ["ARS", "ARS"],
        "side": ["BUY", "SELL"],
        "price": [1500.0, 1510.0],
        "min_amount": [100, 200],
        "max_amount": [1000, 2500],
        "finish_rate": [0.99, 1.0],
        "positive_rate": [1.0, 0.98],
        "merchant_name": ["A", "B"],
        "run_index": [1, 1],
    })
