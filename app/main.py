from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analytics import router as analytics_router
from app.api.v1.market import router as market_router
from app.core.settings import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

frontend_origins = [
    origin.strip()
    for origin in settings.frontend_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(market_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
