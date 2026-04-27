from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.models.lead import Lead, LeadStatus
from app.models.campaign import Campaign, CampaignEmail, EmailStatus
from app.models.subscription import Subscription, SubscriptionStatus, PLAN_LIMITS


def get_dashboard_stats(db: Session, user_id: str) -> dict:
    from app.models.client import Client

    clients = db.query(Client).filter(Client.owner_id == user_id).all()
    client_ids = [c.id for c in clients]

    total_leads = db.query(Lead).filter(Lead.client_id.in_(client_ids)).count()
    new_leads_this_month = db.query(Lead).filter(
        Lead.client_id.in_(client_ids),
        Lead.created_at >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0),
    ).count()

    total_emails_sent = db.query(CampaignEmail).join(Campaign).filter(
        Campaign.client_id.in_(client_ids),
        CampaignEmail.status.in_([EmailStatus.SENT, EmailStatus.OPENED, EmailStatus.CLICKED, EmailStatus.REPLIED]),
    ).count()

    opened = db.query(CampaignEmail).join(Campaign).filter(
        Campaign.client_id.in_(client_ids),
        CampaignEmail.status.in_([EmailStatus.OPENED, EmailStatus.CLICKED, EmailStatus.REPLIED]),
    ).count()

    replied = db.query(CampaignEmail).join(Campaign).filter(
        Campaign.client_id.in_(client_ids),
        CampaignEmail.status == EmailStatus.REPLIED,
    ).count()

    open_rate = (opened / total_emails_sent * 100) if total_emails_sent > 0 else 0
    reply_rate = (replied / total_emails_sent * 100) if total_emails_sent > 0 else 0

    converted = db.query(Lead).filter(
        Lead.client_id.in_(client_ids),
        Lead.status == LeadStatus.CONVERTED,
    ).count()

    return {
        "total_clients": len(clients),
        "total_leads": total_leads,
        "new_leads_this_month": new_leads_this_month,
        "total_emails_sent": total_emails_sent,
        "open_rate": round(open_rate, 1),
        "reply_rate": round(reply_rate, 1),
        "total_converted": converted,
    }


def get_platform_revenue_stats(db: Session) -> dict:
    subs = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).all()
    mrr = sum(PLAN_LIMITS[s.plan]["price_eur"] for s in subs)
    plan_counts = {}
    for s in subs:
        plan_counts[s.plan.value] = plan_counts.get(s.plan.value, 0) + 1

    return {
        "mrr": mrr,
        "total_active_subscriptions": len(subs),
        "plan_distribution": plan_counts,
        "arr": mrr * 12,
        "target_mrr": 30000,
        "progress_pct": round(mrr / 30000 * 100, 1),
    }
