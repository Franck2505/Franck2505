from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.campaign import Campaign, CampaignStatus
from app.models.client import Client

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


class CampaignCreate(BaseModel):
    client_id: str
    name: str
    sequence_days: Optional[List[int]] = [0, 3, 7, 14]


@router.get("/{client_id}")
def list_campaigns(client_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404)
    campaigns = db.query(Campaign).filter(Campaign.client_id == client_id).all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "total_sent": c.total_sent,
            "total_opened": c.total_opened,
            "total_replied": c.total_replied,
            "open_rate": round(c.total_opened / c.total_sent * 100, 1) if c.total_sent else 0,
            "reply_rate": round(c.total_replied / c.total_sent * 100, 1) if c.total_sent else 0,
        }
        for c in campaigns
    ]


@router.post("/")
def create_campaign(req: CampaignCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.subscription import Subscription, SubscriptionStatus, PLAN_LIMITS
    client = db.query(Client).filter(Client.id == req.client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404)

    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub or sub.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=402)

    existing_count = db.query(Campaign).filter(Campaign.client_id == req.client_id).count()
    if existing_count >= PLAN_LIMITS[sub.plan]["campaigns"]:
        raise HTTPException(status_code=429, detail="Campaign limit reached for your plan")

    campaign = Campaign(
        client_id=req.client_id,
        name=req.name,
        sequence_days=req.sequence_days,
        status=CampaignStatus.DRAFT,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return {"id": str(campaign.id), "name": campaign.name, "status": campaign.status}


@router.post("/{campaign_id}/activate")
def activate_campaign(campaign_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from datetime import datetime
    from app.automation.email_pipeline import enqueue_campaign_leads

    campaign = db.query(Campaign).join(Client).filter(
        Campaign.id == campaign_id, Client.owner_id == user.id
    ).first()
    if not campaign:
        raise HTTPException(status_code=404)

    campaign.status = CampaignStatus.ACTIVE
    campaign.started_at = datetime.utcnow()
    db.commit()

    enqueue_campaign_leads(campaign_id, db)
    return {"status": "active", "message": "Campaign activated — emails will be sent automatically"}


@router.post("/{campaign_id}/pause")
def pause_campaign(campaign_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    campaign = db.query(Campaign).join(Client).filter(
        Campaign.id == campaign_id, Client.owner_id == user.id
    ).first()
    if not campaign:
        raise HTTPException(status_code=404)
    campaign.status = CampaignStatus.PAUSED
    db.commit()
    return {"status": "paused"}
