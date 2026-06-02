"""Affiliate program — 20% recurring commission."""
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.affiliate import Affiliate, Referral, AffiliatePayout, PayoutStatus
from app.i18n.locales import get_plan_price

router = APIRouter(prefix="/affiliate", tags=["affiliate"])
COMMISSION_RATE = 0.20


def _generate_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.post("/join")
def join_affiliate_program(db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = db.query(Affiliate).filter(Affiliate.user_id == user.id).first()
    if existing:
        return {"referral_code": existing.referral_code, "message": "Already enrolled"}
    code = _generate_code()
    while db.query(Affiliate).filter(Affiliate.referral_code == code).first():
        code = _generate_code()
    affiliate = Affiliate(user_id=user.id, referral_code=code)
    db.add(affiliate)
    db.commit()
    db.refresh(affiliate)
    return {
        "referral_code": affiliate.referral_code, "commission_rate": "20%",
        "referral_url": f"https://autogrowth.pro/register?ref={affiliate.referral_code}",
        "message": "Welcome to the AutoGrowth Pro affiliate program!",
    }


@router.get("/dashboard")
def affiliate_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    affiliate = db.query(Affiliate).filter(Affiliate.user_id == user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Not enrolled in affiliate program")
    referrals = db.query(Referral).filter(Referral.affiliate_id == affiliate.id).all()
    active_refs = [r for r in referrals if r.is_active]
    monthly_commission = sum(r.commission_eur for r in active_refs)
    pending_payout = round(affiliate.total_earned - affiliate.total_paid, 2)
    return {
        "referral_code": affiliate.referral_code,
        "referral_url": f"https://autogrowth.pro/register?ref={affiliate.referral_code}",
        "commission_rate": f"{int(COMMISSION_RATE * 100)}%",
        "total_referrals": affiliate.total_referrals,
        "active_referrals": len(active_refs),
        "monthly_commission_eur": round(monthly_commission, 2),
        "total_earned": affiliate.total_earned,
        "total_paid": affiliate.total_paid,
        "pending_payout": pending_payout,
        "referrals": [
            {"email": r.referred_user.email[:3] + "***", "plan": r.plan,
             "commission_eur": r.commission_eur, "active": r.is_active, "since": r.created_at}
            for r in referrals
        ],
    }


class PayoutRequest(BaseModel):
    paypal_email: str
    amount: Optional[float] = None


@router.post("/request-payout")
def request_payout(req: PayoutRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    affiliate = db.query(Affiliate).filter(Affiliate.user_id == user.id).first()
    if not affiliate:
        raise HTTPException(status_code=404)
    pending = round(affiliate.total_earned - affiliate.total_paid, 2)
    if pending < 50:
        raise HTTPException(status_code=400, detail=f"Minimum payout is €50. Current balance: €{pending}")
    amount = min(req.amount or pending, pending)
    payout = AffiliatePayout(affiliate_id=affiliate.id, amount=amount,
                              paypal_email=req.paypal_email, status=PayoutStatus.PENDING)
    db.add(payout)
    db.commit()
    return {"status": "requested", "amount": amount, "message": "Payout will be processed within 5 business days"}


def credit_affiliate_commission(referred_user_id: str, plan: str, db: Session):
    from app.models.user import User
    referred_user = db.query(User).filter(User.id == referred_user_id).first()
    if not referred_user or not referred_user.referral_code:
        return
    affiliate = db.query(Affiliate).filter(Affiliate.referral_code == referred_user.referral_code).first()
    if not affiliate:
        return
    plan_price_eur = get_plan_price(plan, "EUR")
    commission = round(plan_price_eur * COMMISSION_RATE, 2)
    ref = Referral(affiliate_id=affiliate.id, referred_user_id=referred_user_id,
                   plan=plan, commission_eur=commission, is_active=True)
    db.add(ref)
    affiliate.total_referrals += 1
    affiliate.total_earned = round(affiliate.total_earned + commission, 2)
    db.commit()
