import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from app.config import settings
from app.i18n.email_templates import (
    get_unsubscribe_text, get_compliance_footer,
    get_welcome_email, get_monthly_report_subject, get_payment_failed_subject,
)
from app.i18n.locales import get_compliance


def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    tracking_id: Optional[str] = None,
    language: str = "fr",
    country: str = "FR",
    unsubscribe_url: Optional[str] = None,
) -> bool:
    try:
        compliance = get_compliance(country)
        full_body = _build_full_body(body_html, language, country, unsubscribe_url, compliance)

        if tracking_id:
            pixel = f'<img src="{settings.FRONTEND_URL}/api/track/open/{tracking_id}" width="1" height="1" style="display:none" />'
            full_body = full_body + pixel

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
        msg["To"] = to_email

        if unsubscribe_url:
            msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
            msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

        msg.attach(MIMEText(full_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[email_service] Failed → {to_email}: {e}")
        return False


def _build_full_body(body: str, language: str, country: str, unsubscribe_url: Optional[str], compliance: dict) -> str:
    footer_parts = []

    if compliance.get("unsubscribe_required") and unsubscribe_url:
        unsub_text = get_unsubscribe_text(language)
        footer_parts.append(f'<a href="{unsubscribe_url}" style="color:#6b7280;font-size:11px;">{unsub_text}</a>')

    compliance_text = get_compliance_footer(language)
    footer_parts.append(f'<span style="color:#9ca3af;font-size:11px;">{compliance_text}</span>')

    if compliance.get("physical_address"):
        footer_parts.append('<span style="color:#9ca3af;font-size:11px;">AutoGrowth Pro SAS — 1 rue de la Paix, 75001 Paris, France</span>')

    footer_html = "<br>".join(footer_parts)

    return f"""
    <div style="font-family:Arial,sans-serif;font-size:14px;line-height:1.6;color:#333;max-width:600px;margin:0 auto">
        {body}
        <hr style="margin:32px 0;border:none;border-top:1px solid #e5e7eb">
        <div style="text-align:center">
            {footer_html}
        </div>
    </div>
    """


def build_unsubscribe_url(lead_id: str, campaign_email_id: str) -> str:
    return f"{settings.FRONTEND_URL}/unsubscribe/{lead_id}/{campaign_email_id}"


def send_welcome_email(to_email: str, full_name: str, plan: str, language: str = "fr", country: str = "FR"):
    tpl = get_welcome_email(language, full_name, plan, settings.FRONTEND_URL)
    send_email(to_email, tpl["subject"], tpl["body"], language=language, country=country)


def send_monthly_report(to_email: str, full_name: str, stats: dict, language: str = "fr", country: str = "FR"):
    month = stats.get("month", "")
    subject = get_monthly_report_subject(language, month)

    stat_rows = "".join(
        f'<tr><td style="padding:8px;border:1px solid #e5e7eb">{k}</td><td style="padding:8px;border:1px solid #e5e7eb"><strong>{v}</strong></td></tr>'
        for k, v in {
            "Leads générés": stats.get("leads_generated", 0),
            "Emails envoyés": stats.get("emails_sent", 0),
            "Taux d'ouverture": f"{stats.get('open_rate', 0):.1f}%",
            "Réponses": stats.get("replies", 0),
            "Conversions": stats.get("conversions", 0),
        }.items()
    )

    body = f"""
    <h2>Rapport — {month}</h2>
    <p>Bonjour {full_name},</p>
    <table style="border-collapse:collapse;width:100%">{stat_rows}</table>
    <p><a href="{settings.FRONTEND_URL}/dashboard" style="background:#6366f1;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;">Voir le rapport complet →</a></p>
    """
    send_email(to_email, subject, body, language=language, country=country)


def send_payment_failed(to_email: str, full_name: str, language: str = "fr", country: str = "FR"):
    subject = get_payment_failed_subject(language)
    body = f"""
    <p>Bonjour {full_name},</p>
    <p>⚠️ Le paiement de votre abonnement a échoué.</p>
    <p><a href="{settings.FRONTEND_URL}/dashboard/billing" style="background:#ef4444;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;">Mettre à jour →</a></p>
    """
    send_email(to_email, subject, body, language=language, country=country)
