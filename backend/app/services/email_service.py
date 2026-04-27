import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from app.config import settings


def send_email(to_email: str, subject: str, body_html: str, tracking_id: Optional[str] = None) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
        msg["To"] = to_email

        # Inject 1px tracking pixel
        if tracking_id:
            pixel = f'<img src="{settings.FRONTEND_URL}/api/track/open/{tracking_id}" width="1" height="1" />'
            body_html = body_html + pixel

        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[email_service] Failed to send to {to_email}: {e}")
        return False


def send_welcome_email(to_email: str, full_name: str, plan: str):
    body = f"""
    <h2>Bienvenue sur AutoGrowth Pro, {full_name} !</h2>
    <p>Votre plan <strong>{plan.upper()}</strong> est actif. Votre machine de croissance est prête.</p>
    <p>Prochaines étapes :</p>
    <ol>
        <li>Créez votre premier client dans le dashboard</li>
        <li>Lancez votre première campagne de prospection</li>
        <li>Regardez les leads arriver automatiquement</li>
    </ol>
    <p><a href="{settings.FRONTEND_URL}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Accéder au Dashboard →</a></p>
    """
    send_email(to_email, "Bienvenue sur AutoGrowth Pro — votre croissance commence maintenant", body)


def send_monthly_report(to_email: str, full_name: str, stats: dict):
    body = f"""
    <h2>Rapport mensuel — {stats.get('month', '')}</h2>
    <p>Bonjour {full_name},</p>
    <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:8px;border:1px solid #e5e7eb">Leads générés</td><td style="padding:8px;border:1px solid #e5e7eb"><strong>{stats.get('leads_generated', 0)}</strong></td></tr>
        <tr><td style="padding:8px;border:1px solid #e5e7eb">Emails envoyés</td><td style="padding:8px;border:1px solid #e5e7eb"><strong>{stats.get('emails_sent', 0)}</strong></td></tr>
        <tr><td style="padding:8px;border:1px solid #e5e7eb">Taux d'ouverture</td><td style="padding:8px;border:1px solid #e5e7eb"><strong>{stats.get('open_rate', 0):.1f}%</strong></td></tr>
        <tr><td style="padding:8px;border:1px solid #e5e7eb">Réponses reçues</td><td style="padding:8px;border:1px solid #e5e7eb"><strong>{stats.get('replies', 0)}</strong></td></tr>
        <tr><td style="padding:8px;border:1px solid #e5e7eb">Conversions</td><td style="padding:8px;border:1px solid #e5e7eb"><strong>{stats.get('conversions', 0)}</strong></td></tr>
    </table>
    <p><a href="{settings.FRONTEND_URL}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Voir le rapport complet →</a></p>
    """
    send_email(to_email, f"Votre rapport mensuel AutoGrowth Pro — {stats.get('month', '')}", body)
