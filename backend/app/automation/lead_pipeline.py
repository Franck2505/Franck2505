"""
Automated lead generation pipeline.
Runs daily: scrape → enrich → score → save.
Respects per-plan monthly limits.
"""
import logging
import asyncio
from app.database import SessionLocal
from app.models.client import Client
from app.models.subscription import Subscription, SubscriptionStatus, PLAN_LIMITS
from app.services.lead_service import generate_leads_for_client

logger = logging.getLogger(__name__)


async def run_lead_generation():
    logger.info("[lead_pipeline] Starting daily lead generation")
    db = SessionLocal()
    try:
        active_subs = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).all()

        for sub in active_subs:
            limit = PLAN_LIMITS[sub.plan]["leads_per_month"]
            remaining = max(0, limit - sub.leads_used_this_month)
            if remaining <= 0:
                continue

            daily_quota = min(remaining, max(5, limit // 20))  # spread over ~20 days
            clients = db.query(Client).filter(
                Client.owner_id == sub.user_id,
                Client.is_active == True,
            ).all()

            for client in clients:
                per_client = max(1, daily_quota // len(clients))
                try:
                    created = await generate_leads_for_client(client, db, max_leads=per_client)
                    sub.leads_used_this_month += created
                    db.commit()
                    logger.info("[lead_pipeline] client=%s created=%d", client.business_name, created)
                except Exception as e:
                    logger.error("[lead_pipeline] client=%s error=%s", client.id, e)
                    db.rollback()

    finally:
        db.close()
    logger.info("[lead_pipeline] Daily lead generation completed")
