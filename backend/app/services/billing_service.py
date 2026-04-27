import stripe
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
from app.models.subscription import Subscription, PlanType, SubscriptionStatus, PLAN_LIMITS
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    PlanType.STARTER: settings.STRIPE_PRICE_STARTER,
    PlanType.GROWTH: settings.STRIPE_PRICE_GROWTH,
    PlanType.PRO: settings.STRIPE_PRICE_PRO,
}


def get_or_create_stripe_customer(user: User) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(email=user.email, name=user.full_name)
    return customer.id


def create_checkout_session(user: User, plan: PlanType, db: Session) -> str:
    customer_id = get_or_create_stripe_customer(user)
    if not user.stripe_customer_id:
        user.stripe_customer_id = customer_id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": PLAN_PRICE_MAP[plan], "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.FRONTEND_URL}/dashboard?checkout=success",
        cancel_url=f"{settings.FRONTEND_URL}/pricing?checkout=cancel",
        metadata={"user_id": str(user.id), "plan": plan.value},
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str, db: Session):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return False

    if event["type"] == "checkout.session.completed":
        _handle_checkout_completed(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_succeeded":
        _handle_payment_succeeded(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_failed":
        _handle_payment_failed(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_canceled(event["data"]["object"], db)

    return True


def _handle_checkout_completed(session_obj: dict, db: Session):
    from app.models.user import User
    user_id = session_obj["metadata"].get("user_id")
    plan_str = session_obj["metadata"].get("plan")
    stripe_sub_id = session_obj.get("subscription")

    if not user_id or not plan_str:
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
    plan = PlanType(plan_str)

    existing = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if existing:
        existing.plan = plan
        existing.status = SubscriptionStatus.ACTIVE
        existing.stripe_subscription_id = stripe_sub_id
        existing.current_period_start = datetime.fromtimestamp(stripe_sub["current_period_start"])
        existing.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"])
        existing.leads_used_this_month = 0
    else:
        sub = Subscription(
            user_id=user.id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            stripe_subscription_id=stripe_sub_id,
            current_period_start=datetime.fromtimestamp(stripe_sub["current_period_start"]),
            current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"]),
        )
        db.add(sub)
    db.commit()


def _handle_payment_succeeded(invoice: dict, db: Session):
    stripe_sub_id = invoice.get("subscription")
    if not stripe_sub_id:
        return
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
    if sub:
        sub.status = SubscriptionStatus.ACTIVE
        sub.leads_used_this_month = 0  # reset monthly counter
        stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
        sub.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"])
        db.commit()


def _handle_payment_failed(invoice: dict, db: Session):
    stripe_sub_id = invoice.get("subscription")
    if not stripe_sub_id:
        return
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
    if sub:
        sub.status = SubscriptionStatus.PAST_DUE
        db.commit()


def _handle_subscription_canceled(stripe_sub: dict, db: Session):
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub["id"]).first()
    if sub:
        sub.status = SubscriptionStatus.CANCELED
        sub.canceled_at = datetime.utcnow()
        db.commit()


def get_monthly_revenue(db: Session) -> float:
    from app.models.subscription import PLAN_LIMITS
    active_subs = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).all()
    total = sum(PLAN_LIMITS[sub.plan]["price_eur"] for sub in active_subs)
    return float(total)
