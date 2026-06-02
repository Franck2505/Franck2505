from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
from app.routers import auth, billing, clients, leads, campaigns, analytics
from app.routers import admin, affiliate, webhooks
from app.automation.scheduler import start_scheduler, stop_scheduler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="AutoGrowth Pro API",
    description="Automated B2B lead generation & outreach — autonomous €30K/month SaaS",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(clients.router)
app.include_router(leads.router)
app.include_router(campaigns.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(affiliate.router)
app.include_router(webhooks.router)


@app.get("/")
def root():
    return {"service": "AutoGrowth Pro API", "version": "2.0.0", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
