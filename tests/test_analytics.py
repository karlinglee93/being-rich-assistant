import pandas as pd
import pytest
from fastapi import HTTPException

from app.services.analytics import compute_annualized_volatility, compute_daily_return, compute_sma


def test_compute_sma_success() -> None:
    series = pd.Series([100, 101, 102, 103, 104])
    result = compute_sma(series, 3)
    assert result == pytest.approx((102 + 103 + 104) / 3)


def test_compute_sma_insufficient_data() -> None:
    series = pd.Series([100, 101])
    with pytest.raises(HTTPException):
        compute_sma(series, 3)


def test_compute_daily_return_success() -> None:
    series = pd.Series([100, 110])
    result = compute_daily_return(series)
    assert result == pytest.approx(0.1)


def test_compute_annualized_volatility_non_negative() -> None:
    series = pd.Series([100, 101, 99, 102, 100])
    result = compute_annualized_volatility(series)
    assert result >= 0
