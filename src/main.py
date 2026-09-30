from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import src.adapters.repositories.models  # Register models with Base
from src.infra.database import Base, engine
from src.adapters.controllers.api_router import router

# Create DB tables at import time so engine/Base tables exist immediately
Base.metadata.create_all(bind=engine)

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.infra.database import SessionLocal
    from src.adapters.repositories.sqlalchemy_repositories import (
        SQLAlchemyPeriodoLetivoRepository,
        SQLAlchemyAtribuicaoRepository,
        SQLAlchemyDidacticPlanRepository,
        SQLAlchemyUserRepository,
        SQLAlchemyNotificationRepository
    )
    from src.adapters.notifiers.strategy_notifiers import EmailSmtpNotifier, TelegramNotifier
    from src.application.use_cases.notification_use_cases import DetectarNotificarAtrasosUseCase

    async def daily_delay_check():
        db = SessionLocal()
        try:
            uc = DetectarNotificarAtrasosUseCase(
                SQLAlchemyPeriodoLetivoRepository(db),
                SQLAlchemyAtribuicaoRepository(db),
                SQLAlchemyDidacticPlanRepository(db),
                SQLAlchemyUserRepository(db),
                SQLAlchemyNotificationRepository(db),
                EmailSmtpNotifier(),
                TelegramNotifier()
            )
            await uc.execute()
        finally:
            db.close()

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

app.include_router(router, prefix="/api")
