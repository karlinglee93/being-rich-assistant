from datetime import date

from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    sma_window: int = Field(default=5)
    sma: float
    daily_return: float
    annualized_volatility: float
