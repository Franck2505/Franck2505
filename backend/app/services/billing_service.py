import stripe
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
from app.models.subscription import Subscription, PlanType, SubscriptionStatus, PLAN_LIMITS
from app.i18n.locales import get_plan_price, get_currency_for_country, CURRENCIES
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

# Static Stripe price IDs per plan (set in .env)
_STATIC_PRICE_MAP = {
    PlanType.STARTER: settings.STRIPE_PRICE_STARTER,
    PlanType.GROWTH:  settings.STRIPE_PRICE_GROWTH,
    PlanType.PRO:     settings.STRIPE_PRICE_PRO,
}


def get_or_create_stripe_customer(user: User, db: Session) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name,
        metadata={"user_id": str(user.id), "country": user.country, "language": user.language},
    )
    user.stripe_customer_id = customer.id
    db.commit()
    return customer.id


def create_checkout_session(user: User, plan: PlanType, db: Session) -> str:
    customer_id = get_or_create_stripe_customer(user, db)
    currency = user.currency.lower()
    amount = get_plan_price(plan.value, user.currency)

    # Try to use a Stripe Price object; fall back to ad-hoc price_data for multi-currency
    static_price_id = _STATIC_PRICE_MAP.get(plan, "")
    if static_price_id and static_price_id != "price_placeholder_starter" and currency == "eur":
        line_items = [{"price": static_price_id, "quantity": 1}]
    else:
        # Dynamic price creation (no price ID needed per currency)
        line_items = [{
            "price_data": {
                "currency": currency,
                "unit_amount": amount * 100,  # Stripe uses cents
                "recurring": {"interval": "month"},
                "product_data": {
                    "name": f"AutoGrowth Pro — {plan.value.capitalize()}",
                    "description": f"{PLAN_LIMITS[plan]['leads_per_month']} leads/month",
                },
            },
            "quantity": 1,
        }]

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=line_items,
        mode="subscription",
        success_url=f"{settings.FRONTEND_URL}/dashboard?checkout=success",
        cancel_url=f"{settings.FRONTEND_URL}/pricing?checkout=cancel",
        locale=user.language if user.language in ["fr","en","es","de","it","pt","nl"] else "auto",
        metadata={"user_id": str(user.id), "plan": plan.value},
        customer_update={"address": "auto"},
        automatic_tax={"enabled": False},
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str, db: Session):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return False

    handlers = {
        "checkout.session.completed": _handle_checkout_completed,
        "invoice.payment_succeeded": _handle_payment_succeeded,
        "invoice.payment_failed": _handle_payment_failed,
        "customer.subscription.deleted": _handle_subscription_canceled,
    }
    handler = handlers.get(event["type"])
    if handler:
        handler(event["data"]["object"], db)
    return True


def _handle_checkout_completed(session_obj: dict, db: Session):
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
        db.add(Subscription(
            user_id=user.id, plan=plan, status=SubscriptionStatus.ACTIVE,
            stripe_subscription_id=stripe_sub_id,
            current_period_start=datetime.fromtimestamp(stripe_sub["current_period_start"]),
            current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"]),
        ))
    from app.services.email_service import send_welcome_email
    send_welcome_email(user.email, user.full_name or "", plan_str, user.language, user.country)
    db.commit()


def _handle_payment_succeeded(invoice: dict, db: Session):
    stripe_sub_id = invoice.get("subscription")
    if not stripe_sub_id:
        return
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
    if sub:
        sub.status = SubscriptionStatus.ACTIVE
        sub.leads_used_this_month = 0
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
        user = db.query(User).filter(User.id == sub.user_id).first()
        if user:
            from app.services.email_service import send_payment_failed
            send_payment_failed(user.email, user.full_name or "", user.language, user.country)


def _handle_subscription_canceled(stripe_sub: dict, db: Session):
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub["id"]).first()
    if sub:
        sub.status = SubscriptionStatus.CANCELED
        sub.canceled_at = datetime.utcnow()
        db.commit()


def get_monthly_revenue_by_currency(db: Session) -> dict:
    from app.i18n.locales import get_plan_price
    active_subs = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).all()
    by_currency: dict[str, float] = {}
    eur_total = 0.0
    for sub in active_subs:
        user = db.query(User).filter(User.id == sub.user_id).first()
        currency = user.currency if user else "EUR"
        price = get_plan_price(sub.plan.value, currency)
        by_currency[currency] = by_currency.get(currency, 0) + price
        eur_price = get_plan_price(sub.plan.value, "EUR")
        eur_total += eur_price

    return {
        "mrr_eur_equivalent": eur_total,
        "mrr_by_currency": by_currency,
        "total_active_subscriptions": len(active_subs),
        "target_mrr_eur": 30000,
        "progress_pct": round(eur_total / 30000 * 100, 1),
    }
