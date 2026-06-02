"""
Automated email campaign pipeline.
Every 30 min: finds due emails → generates multilingual copy → sends with compliance footer.
Respects timezone-aware optimal send windows.
"""
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.database import SessionLocal
from app.models.campaign import Campaign, CampaignEmail, EmailStatus, CampaignStatus
from app.models.lead import Lead, LeadStatus
from app.services.ai_service import generate_cold_email
from app.services.email_service import send_email, build_unsubscribe_url, _build_full_body
from app.i18n.locales import OPTIMAL_SEND_HOURS, get_country_config

logger = logging.getLogger(__name__)
MAX_EMAILS_PER_RUN = 200


def _is_good_send_time(timezone_str: str) -> bool:
    """Return True if current local time is within business hours (Mon-Fri, 8-18h)."""
    try:
        tz = ZoneInfo(timezone_str)
        local_now = datetime.now(tz)
        if local_now.weekday() >= 5:  # Sat/Sun
            return False
        return 8 <= local_now.hour < 18
    except Exception:
        return True  # fail open


async def run_email_campaigns():
    logger.info("[email_pipeline] Starting send batch")
    db = SessionLocal()
    sent_count = 0

    try:
        now = datetime.utcnow()
        due_emails = (
            db.query(CampaignEmail)
            .join(Campaign)
            .filter(
                Campaign.status == CampaignStatus.ACTIVE,
                CampaignEmail.status == EmailStatus.PENDING,
                CampaignEmail.scheduled_at <= now,
            )
            .limit(MAX_EMAILS_PER_RUN)
            .all()
        )

        for campaign_email in due_emails:
            lead = campaign_email.lead
            campaign = campaign_email.campaign
            client = campaign.client

            # Respect local business hours of the target country
            client_tz = client.timezone or "UTC"
            if not _is_good_send_time(client_tz):
                continue

            if not lead.email or not lead.is_email_verified:
                campaign_email.status = EmailStatus.BOUNCED
                db.commit()
                continue

            try:
                lang = client.language or "fr"
                country = client.country or "FR"

                generated = generate_cold_email(
                    sender_business=client.business_name,
                    prospect_name=lead.contact_name or "",
                    prospect_business=lead.business_name,
                    sector=client.sector.value,
                    sequence_step=campaign_email.sequence_step,
                    language=lang,
                )

                subject = generated["subject"]
                raw_body = _html_wrap(generated["body"])
                unsub_url = build_unsubscribe_url(str(lead.id), str(campaign_email.id))

                ok = send_email(
                    to_email=lead.email,
                    subject=subject,
                    body_html=raw_body,
                    tracking_id=campaign_email.tracking_id,
                    language=lang,
                    country=country,
                    unsubscribe_url=unsub_url,
                )

                campaign_email.status = EmailStatus.SENT if ok else EmailStatus.BOUNCED
                campaign_email.subject = subject
                campaign_email.sent_at = now

                if ok:
                    campaign.total_sent += 1
                    lead.last_contacted_at = now
                    if lead.status == LeadStatus.NEW:
                        lead.status = LeadStatus.CONTACTED

                    # Schedule next follow-up
                    seq = campaign.sequence_days or [0, 3, 7, 14]
                    next_step = campaign_email.sequence_step + 1
                    if next_step < len(seq):
                        delay = seq[next_step] - seq[campaign_email.sequence_step]
                        _schedule_followup(db, campaign, lead, next_step, now + timedelta(days=delay))

                    sent_count += 1

                db.commit()

            except Exception as e:
                logger.error("[email_pipeline] id=%s error=%s", campaign_email.id, e)
                db.rollback()

    finally:
        db.close()

    logger.info("[email_pipeline] Sent %d emails", sent_count)


def _schedule_followup(db, campaign: Campaign, lead: Lead, step: int, scheduled_at: datetime):
    if db.query(CampaignEmail).filter(
        CampaignEmail.campaign_id == campaign.id,
        CampaignEmail.lead_id == lead.id,
        CampaignEmail.sequence_step == step,
    ).first():
        return
    db.add(CampaignEmail(
        campaign_id=campaign.id,
        lead_id=lead.id,
        sequence_step=step,
        status=EmailStatus.PENDING,
        scheduled_at=scheduled_at,
    ))


def _html_wrap(text: str) -> str:
    paragraphs = "".join(f"<p>{line}</p>" for line in text.split("\n") if line.strip())
    return f'<div style="font-size:14px;line-height:1.6;color:#333">{paragraphs}</div>'


def enqueue_campaign_leads(campaign_id: str, db):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return
    leads = db.query(Lead).filter(
        Lead.client_id == campaign.client_id,
        Lead.email.isnot(None),
        Lead.is_email_verified == True,
        Lead.status == LeadStatus.NEW,
    ).all()
    now = datetime.utcnow()
    for lead in leads:
        if db.query(CampaignEmail).filter(
            CampaignEmail.campaign_id == campaign_id,
            CampaignEmail.lead_id == lead.id,
            CampaignEmail.sequence_step == 0,
        ).first():
            continue
        db.add(CampaignEmail(
            campaign_id=campaign_id,
            lead_id=lead.id,
            sequence_step=0,
            status=EmailStatus.PENDING,
            scheduled_at=now,
        ))
    db.commit()
