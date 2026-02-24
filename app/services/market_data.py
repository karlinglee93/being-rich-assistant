from datetime import date, timedelta

import pandas as pd
import yfinance as yf
from fastapi import HTTPException, status
from yfinance.exceptions import YFRateLimitError


class MarketDataService:
    def get_latest_price(self, ticker: str) -> tuple[float, str | None]:
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")

        stock = yf.Ticker(normalized_ticker)
        try:
            history = stock.history(period="5d")
        except YFRateLimitError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Market data provider rate limit reached. Please retry shortly.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch market data from provider.",
            ) from exc
        if history.empty:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No data for ticker {normalized_ticker}")

        latest_close = float(history["Close"].dropna().iloc[-1])
        currency = stock.fast_info.get("currency") if hasattr(stock, "fast_info") else None
        return latest_close, currency

    def get_history(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date",
            )

        stock = yf.Ticker(normalized_ticker)
        end_exclusive = end_date + timedelta(days=1)
        try:
            data = stock.history(start=start_date.isoformat(), end=end_exclusive.isoformat())
        except YFRateLimitError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Market data provider rate limit reached. Please retry shortly.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch market data from provider.",
            ) from exc
        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data for ticker {normalized_ticker} in requested range",
            )

        cleaned = data[["Open", "High", "Low", "Close", "Volume"]].dropna().copy()
        cleaned.index = cleaned.index.tz_localize(None) if getattr(cleaned.index, "tz", None) else cleaned.index
        return cleaned
