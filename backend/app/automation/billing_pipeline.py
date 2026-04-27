"""
Billing automation: monthly reports, subscription health checks, dunning.
"""
import logging
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.services.analytics_service import get_dashboard_stats
from app.services.email_service import send_monthly_report, send_email
from app.config import settings

logger = logging.getLogger(__name__)


async def run_monthly_reports():
    logger.info("[billing_pipeline] Sending monthly reports")
    db = SessionLocal()
    try:
        active_subs = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).all()

        month_label = datetime.utcnow().strftime("%B %Y")

        for sub in active_subs:
            user = db.query(User).filter(User.id == sub.user_id).first()
            if not user:
                continue
            try:
                stats = get_dashboard_stats(db, str(sub.user_id))
                stats["month"] = month_label
                send_monthly_report(user.email, user.full_name or "Client", stats)
                logger.info("[billing_pipeline] Report sent to %s", user.email)
            except Exception as e:
                logger.error("[billing_pipeline] user=%s error=%s", user.id, e)
    finally:
        db.close()


async def run_subscription_health_check():
    logger.info("[billing_pipeline] Running subscription health check")
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # Warn users whose subscription ends in 3 days
        expiring_soon = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.current_period_end <= now + timedelta(days=3),
            Subscription.current_period_end > now,
        ).all()

        for sub in expiring_soon:
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                _send_renewal_reminder(user, sub)

        # Dunning: past_due subscriptions — send payment reminder
        past_due = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.PAST_DUE
        ).all()

        for sub in past_due:
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                _send_payment_failed_notice(user)

    finally:
        db.close()


def _send_renewal_reminder(user: User, sub: Subscription):
    end_date = sub.current_period_end.strftime("%d/%m/%Y") if sub.current_period_end else "bientôt"
    body = f"""
    <p>Bonjour {user.full_name or ""},</p>
    <p>Votre abonnement AutoGrowth Pro sera renouvelé le <strong>{end_date}</strong>.</p>
    <p>Tout est en ordre — votre croissance continue sans interruption.</p>
    <p><a href="{settings.FRONTEND_URL}/dashboard/billing">Gérer mon abonnement →</a></p>
    """
    send_email(user.email, "Renouvellement de votre abonnement AutoGrowth Pro", body)


def _send_payment_failed_notice(user: User):
    body = f"""
    <p>Bonjour {user.full_name or ""},</p>
    <p>⚠️ Le paiement de votre abonnement a échoué.</p>
    <p>Mettez à jour vos informations de paiement pour éviter toute interruption de service.</p>
    <p><a href="{settings.FRONTEND_URL}/dashboard/billing" style="background:#ef4444;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;">Mettre à jour mon paiement →</a></p>
    """
    send_email(user.email, "Action requise — Paiement échoué AutoGrowth Pro", body)
