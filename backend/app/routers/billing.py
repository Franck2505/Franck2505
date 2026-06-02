from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.subscription import PlanType
from app.services import billing_service

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: PlanType


@router.post("/checkout")
def create_checkout(req: CheckoutRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    url = billing_service.create_checkout_session(user, req.plan, db)
    return {"checkout_url": url}


@router.get("/subscription")
def get_subscription(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.subscription import Subscription
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        return {"status": "none"}
    return {
        "plan": sub.plan,
        "status": sub.status,
        "leads_used_this_month": sub.leads_used_this_month,
        "current_period_end": sub.current_period_end,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    ok = billing_service.handle_webhook(payload, sig, db)
    if not ok:
        raise HTTPException(status_code=400, detail="Webhook error")
    return {"status": "ok"}


@router.post("/activate-demo")
def activate_demo(plan: str = "growth", db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Activate a subscription without Stripe (dev/demo mode)."""
    from app.models.subscription import Subscription, SubscriptionStatus, PLAN_LIMITS
    from datetime import datetime, timedelta
    try:
        plan_type = PlanType(plan)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        sub = Subscription(user_id=user.id)
        db.add(sub)
    sub.plan = plan_type
    sub.status = SubscriptionStatus.ACTIVE
    sub.current_period_end = datetime.utcnow() + timedelta(days=30)
    sub.leads_used_this_month = 0
    db.commit()
    from app.automation.onboarding_pipeline import init_onboarding
    init_onboarding(str(user.id), db)
    return {"status": "active", "plan": plan_type}


@router.get("/revenue")
def platform_revenue(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return billing_service.get_monthly_revenue(db)
