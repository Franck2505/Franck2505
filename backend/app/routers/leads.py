from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.lead import Lead, LeadStatus
from app.models.client import Client

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/{client_id}")
def list_leads(
    client_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404)

    q = db.query(Lead).filter(Lead.client_id == client_id)
    if status:
        q = q.filter(Lead.status == status)
    leads = q.order_by(Lead.score.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id": str(l.id),
            "business_name": l.business_name,
            "email": l.email,
            "phone": l.phone,
            "status": l.status,
            "score": l.score,
            "source": l.source,
            "created_at": l.created_at,
        }
        for l in leads
    ]


@router.post("/{client_id}/generate")
async def trigger_lead_generation(
    client_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.models.subscription import Subscription, SubscriptionStatus, PLAN_LIMITS
    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404)

    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub or sub.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=402, detail="Active subscription required")

    remaining = PLAN_LIMITS[sub.plan]["leads_per_month"] - sub.leads_used_this_month
    if remaining <= 0:
        raise HTTPException(status_code=429, detail="Monthly lead quota reached")

    from app.services.lead_service import generate_leads_for_client
    background_tasks.add_task(generate_leads_for_client, client, db, min(remaining, 50))

    return {"status": "generating", "remaining_quota": remaining}


@router.patch("/{lead_id}/status")
def update_lead_status(
    lead_id: str,
    status: LeadStatus,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    lead = db.query(Lead).join(Client).filter(Lead.id == lead_id, Client.owner_id == user.id).first()
    if not lead:
        raise HTTPException(status_code=404)
    lead.status = status
    db.commit()
    return {"status": "updated"}


@router.get("/track/open/{tracking_id}")
def track_email_open(tracking_id: str, db: Session = Depends(get_db)):
    from app.models.campaign import CampaignEmail, EmailStatus
    from datetime import datetime
    email = db.query(CampaignEmail).filter(CampaignEmail.tracking_id == tracking_id).first()
    if email and email.status == EmailStatus.SENT:
        email.status = EmailStatus.OPENED
        email.opened_at = datetime.utcnow()
        email.campaign.total_opened += 1
        db.commit()
    # Return 1px transparent GIF
    from fastapi.responses import Response
    pixel = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return Response(content=pixel, media_type="image/gif")
