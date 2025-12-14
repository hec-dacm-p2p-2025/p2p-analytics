import pytest
from p2p_analytics.io import get_processed_root


def test_get_processed_root_returns_a_path():
    root = get_processed_root()
    assert root.exists()  # You may adapt this depending on local paths
