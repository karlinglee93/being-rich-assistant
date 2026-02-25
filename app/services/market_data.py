from datetime import date

import pandas as pd
import requests
from fastapi import HTTPException, status

from app.core.settings import settings


class MarketDataService:
    def __init__(self):
        self.base_url = settings.alpha_vantage_base_url
        self.api_key = settings.alpha_vantage_api_key

    def _validate_credentials(self):
        """Validate that credentials are configured"""
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API credentials not configured. "
                "Set ALPHA_VANTAGE_API_KEY in .env.local"
            )

    def _fetch_alpha_vantage(self, params: dict[str, str]) -> dict:
        request_params = {**params, "apikey": self.api_key}
        try:
            response = requests.get(self.base_url, params=request_params, timeout=15)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unexpected response from Alpha Vantage provider.",
                )

            if payload.get("Note"):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Alpha Vantage rate limit reached. Try again later.",
                )

            if payload.get("Error Message"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticker not found in Alpha Vantage provider.",
                )

            return payload
        except HTTPException:
            raise
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to Alpha Vantage API.",
            ) from exc

    def get_latest_price(self, ticker: str) -> tuple[float, str | None]:
        self._validate_credentials()
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")

        try:
            data = self._fetch_alpha_vantage(
                {
                    "function": "GLOBAL_QUOTE",
                    "symbol": normalized_ticker,
                }
            )

            quote = data.get("Global Quote")
            if not isinstance(quote, dict):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No price data available for ticker {normalized_ticker}",
                )

            price_str = quote.get("05. price")
            if not price_str:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No price data available for ticker {normalized_ticker}",
                )

            price = float(price_str)
            if price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No price data available for ticker {normalized_ticker}",
                )

            return price, "USD"

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch market data from Alpha Vantage provider.",
            ) from exc

    def get_history(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        self._validate_credentials()
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date",
            )

        try:
            data = self._fetch_alpha_vantage(
                {
                    "function": "TIME_SERIES_DAILY_ADJUSTED",
                    "symbol": normalized_ticker,
                    "outputsize": "full",
                }
            )

            series = data.get("Time Series (Daily)")
            if not isinstance(series, dict) or not series:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            records = []
            for day, bar in series.items():
                day_date = date.fromisoformat(day)
                if day_date < start_date or day_date > end_date:
                    continue

                records.append(
                    {
                        "Open": float(bar.get("1. open", 0.0)),
                        "High": float(bar.get("2. high", 0.0)),
                        "Low": float(bar.get("3. low", 0.0)),
                        "Close": float(bar.get("4. close", 0.0)),
                        "Volume": int(float(bar.get("6. volume", 0))),
                        "Date": pd.to_datetime(day),
                    }
                )

            if not records:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            df = pd.DataFrame(records)
            df.set_index("Date", inplace=True)
            df.sort_index(inplace=True)
            df = df[["Open", "High", "Low", "Close", "Volume"]]

            if df.empty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            return df

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch historical data from Alpha Vantage provider.",
            ) from exc
