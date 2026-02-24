from datetime import date

from fastapi import APIRouter, Query

from app.schemas.market import HistoryResponse, LatestPriceResponse, PricePoint
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/market", tags=["market"])
service = MarketDataService()


@router.get("/price", response_model=LatestPriceResponse)
def get_latest_price(ticker: str = Query(..., min_length=1, description="Ticker, e.g. AAPL")) -> LatestPriceResponse:
    price, currency = service.get_latest_price(ticker)
    return LatestPriceResponse(ticker=ticker.upper(), price=price, currency=currency)


@router.get("/history", response_model=HistoryResponse)
def get_history(
    ticker: str = Query(..., min_length=1, description="Ticker, e.g. AAPL"),
    start_date: date = Query(...),
    end_date: date = Query(...),
) -> HistoryResponse:
    data = service.get_history(ticker, start_date, end_date)
    points = [
        PricePoint(
            date=index.date(),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=int(row["Volume"]),
        )
        for index, row in data.iterrows()
    ]
    return HistoryResponse(ticker=ticker.upper(), start_date=start_date, end_date=end_date, points=points)
