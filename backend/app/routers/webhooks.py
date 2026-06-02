"""Outgoing webhooks — Zapier, Make, n8n real-time events."""
import hmac, hashlib, json, logging, secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import httpx
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.ab_test import WebhookEndpoint

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

SUPPORTED_EVENTS = [
    "lead.created", "email.sent", "email.opened", "email.replied",
    "campaign.activated", "campaign.completed", "subscription.activated", "subscription.canceled",
]


class WebhookCreate(BaseModel):
    url: str
    events: Optional[list[str]] = None


@router.get("/")
def list_webhooks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    endpoints = db.query(WebhookEndpoint).filter(WebhookEndpoint.user_id == user.id).all()
    return [{"id": str(e.id), "url": e.url, "events": e.events.split(","),
             "is_active": e.is_active, "total_deliveries": e.total_deliveries,
             "total_failures": e.total_failures} for e in endpoints]


@router.post("/")
def create_webhook(req: WebhookCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    events = req.events or SUPPORTED_EVENTS
    secret = secrets.token_hex(32)
    endpoint = WebhookEndpoint(user_id=user.id, url=req.url, secret=secret, events=",".join(events))
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return {"id": str(endpoint.id), "url": endpoint.url, "secret": secret, "events": events,
            "note": "Store the secret — it won't be shown again."}


@router.delete("/{webhook_id}")
def delete_webhook(webhook_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ep = db.query(WebhookEndpoint).filter(WebhookEndpoint.id == webhook_id,
                                           WebhookEndpoint.user_id == user.id).first()
    if not ep:
        raise HTTPException(status_code=404)
    ep.is_active = False
    db.commit()
    return {"status": "disabled"}


@router.get("/events")
def list_supported_events():
    return {"events": SUPPORTED_EVENTS}


async def fire_webhook(user_id: str, event: str, payload: dict, db: Session):
    endpoints = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.user_id == user_id, WebhookEndpoint.is_active == True).all()
    for ep in endpoints:
        if event not in ep.events.split(","):
            continue
        body = json.dumps({"event": event, "timestamp": datetime.utcnow().isoformat(), "data": payload})
        sig = hmac.new(ep.secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(ep.url, content=body, headers={
                    "Content-Type": "application/json",
                    "X-AutoGrowth-Signature": f"sha256={sig}",
                    "X-AutoGrowth-Event": event,
                })
            ep.total_deliveries += 1
            if resp.status_code >= 400:
                ep.total_failures += 1
        except Exception as e:
            ep.total_failures += 1
            logger.warning("[webhook] delivery failed url=%s event=%s err=%s", ep.url, event, e)
    db.commit()
