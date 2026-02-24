from datetime import date, timedelta
from typing import Optional

import pandas as pd
import requests
from fastapi import HTTPException, status

from app.core.settings import settings


class IBKRAPIError(Exception):
    """Raised when IBKR API returns an error"""

    pass


class MarketDataService:
    def __init__(self):
        self.base_url = settings.ibkr_base_url.rstrip("/")
        self.api_key = settings.ibkr_api_key
        self.api_secret = settings.ibkr_api_secret
        self.account_id = settings.ibkr_account_id

    def _validate_credentials(self):
        """Validate that credentials are configured"""
        if not all([self.api_key, self.api_secret, self.account_id]):
            raise ValueError(
                "IBKR API credentials not configured. "
                "Set IBKR_API_KEY, IBKR_API_SECRET, and IBKR_ACCOUNT_ID in .env"
            )

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers for IBKR API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get_contract_id(self, ticker: str) -> Optional[str]:
        """Get IBKR contract ID for a ticker"""
        try:
            url = f"{self.base_url}/iserver/app/scanner/params"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()

            # Search for the contract
            search_url = f"{self.base_url}/iserver/scanner/run"
            search_params = {
                "instrument": ticker,
                "type": "stocks",
            }
            search_response = requests.post(
                search_url,
                json=search_params,
                headers=self._get_headers(),
                timeout=10,
            )
            search_response.raise_for_status()

            data = search_response.json()
            if data and len(data) > 0:
                return data[0].get("conId")
            return None

        except requests.RequestException:
            return None

    def get_latest_price(self, ticker: str) -> tuple[float, str | None]:
        self._validate_credentials()
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")

        try:
            # IBKR REST API endpoint for market data
            url = f"{self.base_url}/iserver/marketdata/{normalized_ticker}/snapshot"

            response = requests.get(
                url,
                headers=self._get_headers(),
                params={"fields": "last,bid,ask,currency"},
                timeout=10,
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data for ticker {normalized_ticker}",
                )

            response.raise_for_status()
            data = response.json()

            # Extract price from available fields
            price = None
            if isinstance(data, dict):
                # Try different price fields
                price = data.get("last") or data.get("bid") or data.get("ask")
                currency = data.get("currency", "USD")
            elif isinstance(data, list) and len(data) > 0:
                price = (
                    data[0].get("last")
                    or data[0].get("bid")
                    or data[0].get("ask")
                )
                currency = data[0].get("currency", "USD")

            if not price or price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No price data available for ticker {normalized_ticker}",
                )

            return float(price), currency or "USD"

        except HTTPException:
            raise
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to IBKR API. Check credentials and API status.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch market data from IBKR provider.",
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
            # IBKR API endpoint for historical data
            url = f"{self.base_url}/iserver/marketdata/history"

            params = {
                "conid": normalized_ticker,
                "period": "1d",
                "bar": "1d",
                "startDate": start_date.isoformat(),
                "endDate": (end_date + timedelta(days=1)).isoformat(),
            }

            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10,
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data for ticker {normalized_ticker}",
                )

            response.raise_for_status()
            data = response.json()

            # Parse historical data
            if not data or "data" not in data or not data["data"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            # Convert to DataFrame
            records = []
            for bar in data["data"]:
                records.append(
                    {
                        "Open": bar.get("o", 0),
                        "High": bar.get("h", 0),
                        "Low": bar.get("l", 0),
                        "Close": bar.get("c", 0),
                        "Volume": bar.get("v", 0),
                        "Date": pd.to_datetime(bar.get("t", 0), unit="s"),
                    }
                )

            df = pd.DataFrame(records)
            df.set_index("Date", inplace=True)
            df = df[["Open", "High", "Low", "Close", "Volume"]]

            # Filter to requested date range
            df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]

            if df.empty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            return df

        except HTTPException:
            raise
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to IBKR API. Check credentials and API status.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch historical data from IBKR provider.",
            ) from exc
