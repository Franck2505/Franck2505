from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.client import Client, BusinessSector

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientCreate(BaseModel):
    business_name: str
    sector: BusinessSector
    target_location: Optional[str] = "France"
    target_keywords: Optional[List[str]] = []
    website: Optional[str] = None


@router.get("/")
def list_clients(db: Session = Depends(get_db), user=Depends(get_current_user)):
    clients = db.query(Client).filter(Client.owner_id == user.id).all()
    return [{"id": str(c.id), "business_name": c.business_name, "sector": c.sector, "is_active": c.is_active} for c in clients]


@router.post("/")
def create_client(req: ClientCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.subscription import Subscription, SubscriptionStatus
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub or sub.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=402, detail="Active subscription required")

    client = Client(
        owner_id=user.id,
        business_name=req.business_name,
        sector=req.sector,
        target_location=req.target_location,
        target_keywords=req.target_keywords,
        website=req.website,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"id": str(client.id), "business_name": client.business_name}


@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    client = db.query(Client).filter(Client.id == client_id, Client.owner_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404)
    client.is_active = False
    db.commit()
    return {"status": "deactivated"}
