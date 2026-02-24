from datetime import date

from fastapi import APIRouter, Query

from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics import compute_annualized_volatility, compute_daily_return, compute_sma
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/analytics", tags=["analytics"])
service = MarketDataService()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    ticker: str = Query(..., min_length=1, description="Ticker, e.g. AAPL"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    sma_window: int = Query(5, gt=0),
) -> AnalyticsSummaryResponse:
    data = service.get_history(ticker, start_date, end_date)
    close_series = data["Close"]

    sma = compute_sma(close_series, sma_window)
    daily_return = compute_daily_return(close_series)
    annualized_volatility = compute_annualized_volatility(close_series)

    return AnalyticsSummaryResponse(
        ticker=ticker.upper(),
        start_date=start_date,
        end_date=end_date,
        sma_window=sma_window,
        sma=sma,
        daily_return=daily_return,
        annualized_volatility=annualized_volatility,
    )
