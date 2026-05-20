"""Main FastAPI application."""

from fastapi import FastAPI
from app.config import settings
from app.db import Base, engine
from app.api.auth import router as auth_router
from app.api.reports import router as reports_router
from app.api.users import router as users_router
from app.api.payments import router as payments_router

# Create tables
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    await engine.dispose()


# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(reports_router)
app.include_router(users_router)
