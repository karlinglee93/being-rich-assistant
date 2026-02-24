from datetime import date, timedelta
from typing import Optional

import pandas as pd
from fastapi import HTTPException, status
from ib_insync import IB, Stock, util

from app.core.settings import settings


class IBKRConnectionError(Exception):
    """Raised when unable to connect to IBKR API"""

    pass


class MarketDataService:
    def __init__(self):
        self.ib: Optional[IB] = None

    def _get_connection(self) -> IB:
        """Get or create connection to IBKR API"""
        if self.ib is None or not self.ib.isConnected():
            self.ib = IB()
            try:
                self.ib.connect(
                    host=settings.ibkr_host,
                    port=settings.ibkr_port,
                    clientId=1,
                    timeout=settings.ibkr_timeout_seconds,
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to connect to IBKR API. Ensure TWS/Gateway is running.",
                ) from exc
        return self.ib

    def get_latest_price(self, ticker: str) -> tuple[float, str | None]:
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")

        try:
            ib = self._get_connection()

            # Create a stock contract for the ticker
            contract = Stock(symbol=normalized_ticker, exchange="SMART", currency="USD")

            # Request market data
            ib.qualifyContracts(contract)
            if not contract.conId:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data for ticker {normalized_ticker}",
                )

            # Get ticker data
            ticker_obj = ib.reqMktData(contract, "", False, False)
            ib.sleep(1)  # Wait for data to arrive

            if ticker_obj.last and ticker_obj.last > 0:
                latest_price = ticker_obj.last
            elif ticker_obj.bid and ticker_obj.bid > 0:
                latest_price = ticker_obj.bid
            elif ticker_obj.ask and ticker_obj.ask > 0:
                latest_price = ticker_obj.ask
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No price data available for ticker {normalized_ticker}",
                )

            ib.cancelMktData(contract)
            currency = contract.currency or "USD"
            return float(latest_price), currency

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch market data from IBKR provider.",
            ) from exc

    def get_history(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date",
            )

        try:
            ib = self._get_connection()

            # Create a stock contract for the ticker
            contract = Stock(symbol=normalized_ticker, exchange="SMART", currency="USD")

            # Qualify contract
            ib.qualifyContracts(contract)
            if not contract.conId:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No data for ticker {normalized_ticker}",
                )

            # Request historical data
            duration = f"{(end_date - start_date).days + 1} D"
            bars = ib.reqHistoricalData(
                contract=contract,
                endDateTime=end_date.isoformat(),
                durationStr=duration,
                barSizeSetting="1 day",
                whatToShow="TRADES",
                useRTH=True,
                formatDate=1,
                timeout=settings.ibkr_timeout_seconds,
            )

            if not bars:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            # Convert bars to DataFrame
            df = util.df(bars)

            # Ensure we have the required columns
            required_cols = ["open", "high", "low", "close", "volume"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Retrieved data missing required OHLCV columns",
                )

            # Rename columns to match expected output
            data = df[required_cols].copy()
            data.columns = ["Open", "High", "Low", "Close", "Volume"]
            data.index = pd.to_datetime(df.index)
            data.index = data.index.tz_localize(None) if getattr(data.index, "tz", None) else data.index

            # Filter to requested date range
            data = data[(data.index.date >= start_date) & (data.index.date <= end_date)]

            if data.empty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data for ticker {normalized_ticker} in requested range",
                )

            return data

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch historical data from IBKR provider.",
            ) from exc

    def close(self):
        """Close IBKR connection"""
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
