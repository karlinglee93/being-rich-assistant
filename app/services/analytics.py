import numpy as np
import pandas as pd
from fastapi import HTTPException, status


def compute_sma(close_series: pd.Series, window: int) -> float:
    if window <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sma_window must be > 0")
    if len(close_series) < window:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough data points for requested sma_window",
        )
    return float(close_series.rolling(window=window).mean().dropna().iloc[-1])


def compute_daily_return(close_series: pd.Series) -> float:
    if len(close_series) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least 2 close prices are required")
    returns = close_series.pct_change().dropna()
    return float(returns.iloc[-1])


def compute_annualized_volatility(close_series: pd.Series) -> float:
    if len(close_series) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least 2 close prices are required")
    returns = close_series.pct_change().dropna()
    return float(np.std(returns, ddof=1) * np.sqrt(252))
