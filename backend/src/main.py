import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import src.adapters.repositories.models  # Register models with Base
from src.infra.database import Base, engine, AsyncSessionLocal
from src.adapters.controllers.api_router import router

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from src.adapters.repositories.sqlalchemy_repositories import (
        SQLAlchemyPeriodoLetivoRepository,
        SQLAlchemyAtribuicaoRepository,
        SQLAlchemyDidacticPlanRepository,
        SQLAlchemyUserRepository,
        SQLAlchemyNotificationRepository
    )
    from src.adapters.notifiers.strategy_notifiers import TelegramNotifier, build_email_notifier
    from src.application.use_cases.notification_use_cases import DetectarNotificarAtrasosUseCase

    async def daily_delay_check():
        async with AsyncSessionLocal() as db:
            try:
                uc = DetectarNotificarAtrasosUseCase(
                    SQLAlchemyPeriodoLetivoRepository(db),
                    SQLAlchemyAtribuicaoRepository(db),
                    SQLAlchemyDidacticPlanRepository(db),
                    SQLAlchemyUserRepository(db),
                    SQLAlchemyNotificationRepository(db),
                    build_email_notifier(),
                    TelegramNotifier()
                )
                await uc.execute()
            finally:
                pass  # session closes via async context manager

    scheduler.add_job(daily_delay_check, 'cron', hour=8, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="Sistema de Planos Didáticos - CEFET-MG",
    version="1.0.0",
    description="Sistema para gestão de planos didáticos com FastAPI, Clean Architecture e DDD",
    lifespan=lifespan
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint usado pelo health check do Render."""
    return {"status": "ok"}


app.include_router(router, prefix="/api")
