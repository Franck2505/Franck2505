"""Admin API — MRR, churn, cohorts, user list. Admin role only."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User, UserRole
from app.models.subscription import Subscription, SubscriptionStatus, PLAN_LIMITS
from app.models.lead import Lead
from app.models.campaign import Campaign, CampaignEmail, EmailStatus
from app.models.affiliate import Affiliate
from app.i18n.locales import get_plan_price

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user=Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


@router.get("/metrics")
def platform_metrics(db: Session = Depends(get_db), admin=Depends(require_admin)):
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    active_subs = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).all()
    mrr = sum(
        get_plan_price(s.plan.value, db.query(User).filter(User.id == s.user_id).first().currency or "EUR")
        for s in active_subs
    )

    churned = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.CANCELED,
        Subscription.canceled_at >= month_start,
    ).count()

    new_subs = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.created_at >= month_start,
    ).count()

    total_users = db.query(User).count()
    total_leads = db.query(Lead).count()
    total_sent = db.query(CampaignEmail).filter(
        CampaignEmail.status.in_([EmailStatus.SENT, EmailStatus.OPENED, EmailStatus.REPLIED])
    ).count()
    total_opens = db.query(CampaignEmail).filter(
        CampaignEmail.status.in_([EmailStatus.OPENED, EmailStatus.REPLIED])
    ).count()

    plan_dist = {}
    for sub in active_subs:
        plan_dist[sub.plan.value] = plan_dist.get(sub.plan.value, 0) + 1

    currency_mrr: dict[str, float] = {}
    for sub in active_subs:
        u = db.query(User).filter(User.id == sub.user_id).first()
        cur = u.currency if u else "EUR"
        price = get_plan_price(sub.plan.value, cur)
        currency_mrr[cur] = currency_mrr.get(cur, 0) + price

    return {
        "mrr_eur": round(mrr, 2),
        "arr_eur": round(mrr * 12, 2),
        "target_mrr": 30000,
        "progress_pct": round(mrr / 30000 * 100, 1),
        "active_subscriptions": len(active_subs),
        "new_subs_this_month": new_subs,
        "churned_this_month": churned,
        "churn_rate_pct": round(churned / max(len(active_subs), 1) * 100, 1),
        "total_users": total_users,
        "total_leads": total_leads,
        "total_emails_sent": total_sent,
        "overall_open_rate": round(total_opens / max(total_sent, 1) * 100, 1),
        "plan_distribution": plan_dist,
        "mrr_by_currency": currency_mrr,
        "ltv_estimate": round(mrr / max(len(active_subs), 1) / 0.05, 2),
    }


@router.get("/users")
def list_users(
    page: int = 1, per_page: int = 50, search: str = "",
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    q = db.query(User)
    if search:
        q = q.filter(User.email.ilike(f"%{search}%"))
    total = q.count()
    users = q.offset((page - 1) * per_page).limit(per_page).all()
    result = []
    for u in users:
        sub = u.subscription
        result.append({
            "id": str(u.id), "email": u.email, "full_name": u.full_name,
            "country": u.country, "language": u.language, "currency": u.currency,
            "plan": sub.plan.value if sub else None,
            "sub_status": sub.status.value if sub else None,
            "leads_used": sub.leads_used_this_month if sub else 0,
            "created_at": u.created_at,
        })
    return {"total": total, "page": page, "users": result}


@router.get("/cohorts")
def cohort_analysis(db: Session = Depends(get_db), admin=Depends(require_admin)):
    now = datetime.utcnow()
    cohorts = []
    for months_ago in range(6):
        start = (now.replace(day=1) - timedelta(days=months_ago * 30)).replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
        new_users = db.query(User).filter(User.created_at >= start, User.created_at < end).count()
        active = db.query(Subscription).filter(
            Subscription.created_at >= start, Subscription.created_at < end,
            Subscription.status == SubscriptionStatus.ACTIVE,
        ).count()
        cohorts.append({
            "month": start.strftime("%Y-%m"), "new_users": new_users,
            "still_active": active, "retention_pct": round(active / max(new_users, 1) * 100, 1),
        })
    return cohorts


@router.get("/revenue/30d")
def revenue_last_30d(db: Session = Depends(get_db), admin=Depends(require_admin)):
    now = datetime.utcnow()
    days = []
    for d in range(29, -1, -1):
        day = now - timedelta(days=d)
        ds = day.replace(hour=0, minute=0, second=0, microsecond=0)
        de = day.replace(hour=23, minute=59, second=59)
        new_subs = db.query(Subscription).filter(
            Subscription.created_at >= ds, Subscription.created_at <= de,
            Subscription.status == SubscriptionStatus.ACTIVE,
        ).all()
        daily_mrr = sum(PLAN_LIMITS[s.plan.value]["price_eur"] for s in new_subs)
        days.append({"date": day.strftime("%Y-%m-%d"), "new_mrr": daily_mrr, "new_subs": len(new_subs)})
    return days


@router.get("/affiliates")
def affiliate_stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    affiliates = db.query(Affiliate).all()
    return [
        {
            "id": str(a.id), "email": a.user.email, "referral_code": a.referral_code,
            "total_referrals": a.total_referrals, "total_earned": a.total_earned,
            "total_paid": a.total_paid, "pending_payout": round(a.total_earned - a.total_paid, 2),
        }
        for a in affiliates
    ]


@router.post("/users/{user_id}/impersonate")
def impersonate_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    from app.services.auth_service import create_access_token
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    token = create_access_token({"sub": user.email, "impersonated_by": str(admin.id)}, expires_delta=timedelta(hours=1))
    return {"access_token": token, "impersonated_user": user.email}


@router.patch("/users/{user_id}/role")
def set_user_role(user_id: str, role: UserRole, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    user.role = role
    db.commit()
    return {"status": "updated", "email": user.email, "role": role}
