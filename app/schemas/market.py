from datetime import date

from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class LatestPriceResponse(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    price: float = Field(description="Latest close/market price")
    currency: str | None = Field(default=None)


class HistoryResponse(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    points: list[PricePoint]
