from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.client import Client, BusinessSector
from app.i18n.locales import get_country_config

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientCreate(BaseModel):
    business_name: str
    sector: BusinessSector
    target_location: Optional[str] = None
    target_keywords: Optional[List[str]] = []
    website: Optional[str] = None
    country: Optional[str] = None       # defaults to user's country
    language: Optional[str] = None      # defaults to user's language
    timezone: Optional[str] = None


@router.get("/")
def list_clients(db: Session = Depends(get_db), user=Depends(get_current_user)):
    clients = db.query(Client).filter(Client.owner_id == user.id).all()
    return [
        {
            "id": str(c.id),
            "business_name": c.business_name,
            "sector": c.sector,
            "is_active": c.is_active,
            "country": c.country,
            "language": c.language,
            "timezone": c.timezone,
        }
        for c in clients
    ]


@router.post("/")
def create_client(req: ClientCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.subscription import Subscription, SubscriptionStatus
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub or sub.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=402, detail="Active subscription required")

    country = (req.country or user.country or "FR").upper()
    config = get_country_config(country)
    language = req.language or user.language or config["language"]
    timezone = req.timezone or user.timezone or config["timezone"]
    location = req.target_location or config["name"]

    client = Client(
        owner_id=user.id,
        business_name=req.business_name,
        sector=req.sector,
        target_location=location,
        target_keywords=req.target_keywords,
        website=req.website,
        country=country,
        language=language,
        timezone=timezone,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"id": str(client.id), "business_name": client.business_name, "country": client.country, "language": client.language}


@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404)
    client.is_active = False
    db.commit()
    return {"status": "deactivated"}
