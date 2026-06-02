"""
Central scheduler — runs all automated jobs.
Runs as a background process alongside the FastAPI app.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Europe/Paris")


def start_scheduler():
    from app.automation.lead_pipeline import run_lead_generation
    from app.automation.email_pipeline import run_email_campaigns
    from app.automation.billing_pipeline import run_monthly_reports, run_subscription_health_check
    from app.automation.onboarding_pipeline import run_onboarding_emails

    # Generate leads every day at 03:00
    scheduler.add_job(
        run_lead_generation,
        CronTrigger(hour=3, minute=0),
        id="lead_generation",
        replace_existing=True,
    )

    # Send scheduled campaign emails every 30 minutes
    scheduler.add_job(
        run_email_campaigns,
        IntervalTrigger(minutes=30),
        id="email_campaigns",
        replace_existing=True,
    )

    # Monthly reports on the 1st at 08:00
    scheduler.add_job(
        run_monthly_reports,
        CronTrigger(day=1, hour=8, minute=0),
        id="monthly_reports",
        replace_existing=True,
    )

    # Subscription health check daily at 06:00
    scheduler.add_job(
        run_subscription_health_check,
        CronTrigger(hour=6, minute=0),
        id="subscription_health",
        replace_existing=True,
    )

    # Onboarding emails daily at 09:00
    scheduler.add_job(
        run_onboarding_emails,
        CronTrigger(hour=9, minute=0),
        id="onboarding_emails",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))


def stop_scheduler():
    scheduler.shutdown(wait=False)
