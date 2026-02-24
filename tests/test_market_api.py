from datetime import date

import pandas as pd
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from yfinance.exceptions import YFRateLimitError

from app.main import app
from app.services.market_data import MarketDataService

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_price_mocked(monkeypatch) -> None:
    def mock_get_latest_price(self, ticker: str):
        return 123.45, "USD"

    monkeypatch.setattr(MarketDataService, "get_latest_price", mock_get_latest_price)

    response = client.get("/api/v1/market/price", params={"ticker": "AAPL"})
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
    assert response.json()["price"] == 123.45
    assert response.json()["currency"] == "USD"


def test_get_history_mocked(monkeypatch) -> None:
    index = pd.to_datetime(["2026-01-02", "2026-01-03"])
    frame = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000000, 1100000],
        },
        index=index,
    )

    def mock_get_history(self, ticker: str, start_date: date, end_date: date):
        return frame

    monkeypatch.setattr(MarketDataService, "get_history", mock_get_history)

    response = client.get(
        "/api/v1/market/history",
        params={"ticker": "AAPL", "start_date": "2026-01-01", "end_date": "2026-01-10"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert len(payload["points"]) == 2
    assert payload["points"][0]["close"] == 101.0


def test_market_data_service_get_history_date_range_inclusive(monkeypatch) -> None:
    class _MockTicker:
        def history(self, start: str, end: str):
            assert start == "2026-02-01"
            assert end == "2026-02-04"
            return pd.DataFrame(
                {
                    "Open": [100.0],
                    "High": [101.0],
                    "Low": [99.0],
                    "Close": [100.5],
                    "Volume": [1000000],
                },
                index=pd.to_datetime(["2026-02-03"]),
            )

    monkeypatch.setattr("app.services.market_data.yf.Ticker", lambda ticker: _MockTicker())

    service = MarketDataService()
    data = service.get_history("AAPL", date(2026, 2, 1), date(2026, 2, 3))

    assert not data.empty
    assert float(data.iloc[0]["Close"]) == 100.5


def test_market_data_service_get_history_rate_limit_returns_http_error(monkeypatch) -> None:
    class _MockTicker:
        def history(self, start: str, end: str):
            raise YFRateLimitError()

    monkeypatch.setattr("app.services.market_data.yf.Ticker", lambda ticker: _MockTicker())

    service = MarketDataService()
    with pytest.raises(HTTPException) as exc_info:
        service.get_history("AAPL", date(2026, 2, 1), date(2026, 2, 3))

    assert exc_info.value.status_code == 503


def test_get_analytics_summary_mocked(monkeypatch) -> None:
    index = pd.to_datetime(["2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05", "2026-01-06"])
    frame = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "High": [101.0, 102.0, 103.0, 104.0, 105.0],
            "Low": [99.0, 100.0, 101.0, 102.0, 103.0],
            "Close": [100.0, 101.0, 102.0, 103.0, 104.0],
            "Volume": [1000000, 1000000, 1000000, 1000000, 1000000],
        },
        index=index,
    )

    def mock_get_history(self, ticker: str, start_date: date, end_date: date):
        return frame

    monkeypatch.setattr(MarketDataService, "get_history", mock_get_history)

    response = client.get(
        "/api/v1/analytics/summary",
        params={"ticker": "AAPL", "start_date": "2026-01-01", "end_date": "2026-01-10", "sma_window": 3},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert payload["sma_window"] == 3
    assert isinstance(payload["sma"], float)
    assert isinstance(payload["daily_return"], float)
    assert isinstance(payload["annualized_volatility"], float)
