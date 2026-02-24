from fastapi import FastAPI

from app.api.v1.analytics import router as analytics_router
from app.api.v1.market import router as market_router
from app.core.settings import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(market_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
