"""7-email onboarding sequence — FR + EN. Days 0,1,3,7,14,21,30."""
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models.onboarding import OnboardingProgress
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionStatus
from app.services.email_service import send_email
from app.config import settings

logger = logging.getLogger(__name__)

ONBOARDING_DELAY_DAYS = [0, 1, 3, 7, 14, 21, 30]

ONBOARDING_EMAILS = {
    "fr": [
        {
            "subject": "🚀 Votre machine de croissance est prête — 3 étapes pour démarrer",
            "body": lambda name, url: f"""
            <h2>Bonjour {name} 👋</h2>
            <p>Votre compte AutoGrowth Pro est actif. Lancez votre première campagne en moins de 10 minutes :</p>
            <ol><li><strong>Créez un client</strong></li><li><strong>Générez des leads</strong></li><li><strong>Activez une campagne</strong></li></ol>
            <p><a href="{url}/dashboard/clients" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none">Créer mon premier client →</a></p>
            """,
        },
        {
            "subject": "Avez-vous créé votre premier client ? (2 min)",
            "body": lambda name, url: f"<p>Bonjour {name},</p><p>La première étape : <strong>créer un client</strong> avec votre secteur et zone cible.</p><p><a href='{url}/dashboard/clients'>Configurer mon client →</a></p>",
        },
        {
            "subject": "5 bonnes pratiques pour doubler votre taux de réponse",
            "body": lambda name, url: f"<p>Bonjour {name},</p><ul><li>✅ Ciblez des niches précises</li><li>✅ Activez les 4 relances</li><li>✅ Objet court — moins de 6 mots</li><li>✅ CTA unique</li><li>✅ Envoi mardi-jeudi</li></ul><p><a href='{url}/dashboard'>Voir mes campagnes →</a></p>",
        },
        {
            "subject": "Thomas a obtenu 3 clients en 3 semaines — voici comment",
            "body": lambda name, url: f"<p>Bonjour {name},</p><p>Thomas, consultant IT à Lyon, a signé son 3ème client 3 semaines après son inscription.</p><p><em>\"J'envoyais 50 emails/semaine à la main. Avec AutoGrowth, c'est 300/semaine.\"</em></p><p><a href='{url}/dashboard/campaigns'>Dupliquer cette stratégie →</a></p>",
        },
        {
            "subject": "Vos 2 premières semaines — bilan et prochaines étapes",
            "body": lambda name, url: f"<p>Bonjour {name},</p><p>2 semaines après votre inscription — ajoutez un 2ème secteur cible et testez l'A/B test.</p><p><a href='{url}/analytics/dashboard'>Voir mon bilan →</a></p>",
        },
        {
            "subject": "Vous approchez de votre limite mensuelle — passez au plan supérieur",
            "body": lambda name, url: f"<p>Bonjour {name},</p><p>Passez au plan <strong>Pro</strong> pour des leads et campagnes illimités.</p><p><a href='{url}/dashboard/billing' style='background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none'>Passer au Pro →</a></p>",
        },
        {
            "subject": "1 question rapide — comment se passe AutoGrowth Pro ?",
            "body": lambda name, url: (
                "<p>Bonjour " + name + ",</p><p>Un mois s'est passé. Sur une échelle de 0 à 10, recommanderiez-vous AutoGrowth Pro ?</p><div style='margin:20px 0'>"
                + "".join("<a href='" + url + "/nps?score=" + str(i) + "' style='background:#f3f4f6;padding:8px 14px;border-radius:8px;text-decoration:none;color:#374151;font-weight:bold;margin:2px;display:inline-block'>" + str(i) + "</a>" for i in range(11))
                + "</div>"
            ),
        },
    ],
    "en": [
        {
            "subject": "🚀 Your growth machine is ready — 3 steps to get started",
            "body": lambda name, url: f"""
            <h2>Hello {name} 👋</h2>
            <p>Your AutoGrowth Pro account is active. Launch your first campaign in under 10 minutes:</p>
            <ol><li><strong>Create a client</strong></li><li><strong>Generate leads</strong></li><li><strong>Activate a campaign</strong></li></ol>
            <p><a href="{url}/dashboard/clients" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none">Create my first client →</a></p>
            """,
        },
        {
            "subject": "Did you create your first client? (takes 2 min)",
            "body": lambda name, url: f"<p>Hi {name},</p><p>Just checking in — have you set up your first client?</p><p><a href='{url}/dashboard/clients'>Set up my client →</a></p>",
        },
        {
            "subject": "5 best practices to double your reply rate",
            "body": lambda name, url: f"<p>Hi {name},</p><ul><li>✅ Target specific niches</li><li>✅ Enable all 4 follow-ups</li><li>✅ Short subject lines</li><li>✅ Single CTA</li></ul><p><a href='{url}/dashboard'>View my campaigns →</a></p>",
        },
        {
            "subject": "James got 3 new clients in 3 weeks — here's how",
            "body": lambda name, url: f"<p>Hi {name},</p><p>James, an IT consultant in London, closed his 3rd client after 3 weeks.</p><p><a href='{url}/dashboard/campaigns'>Use this strategy →</a></p>",
        },
        {
            "subject": "Your first 2 weeks — results and next steps",
            "body": lambda name, url: f"<p>Hi {name},</p><p>2 weeks in — great progress!</p><p><a href='{url}/analytics/dashboard'>View my results →</a></p>",
        },
        {
            "subject": "You're approaching your monthly limit — upgrade for unlimited",
            "body": lambda name, url: f"<p>Hi {name},</p><p>Upgrade to <strong>Pro</strong> for unlimited leads and campaigns.</p><p><a href='{url}/dashboard/billing' style='background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none'>Upgrade to Pro →</a></p>",
        },
        {
            "subject": "Quick question — how's AutoGrowth Pro going?",
            "body": lambda name, url: (
                "<p>Hi " + name + ",</p><p>One month in! How likely are you to recommend AutoGrowth Pro (0–10)?</p><div style='margin:20px 0'>"
                + "".join("<a href='" + url + "/nps?score=" + str(i) + "' style='background:#f3f4f6;padding:8px 14px;border-radius:8px;text-decoration:none;color:#374151;font-weight:bold;margin:2px;display:inline-block'>" + str(i) + "</a>" for i in range(11))
                + "</div>"
            ),
        },
    ],
}


async def run_onboarding_emails():
    logger.info("[onboarding] Processing onboarding sequences")
    db = SessionLocal()
    sent = 0
    try:
        progresses = db.query(OnboardingProgress).filter(OnboardingProgress.completed == False).all()
        for progress in progresses:
            user = db.query(User).filter(User.id == progress.user_id).first()
            sub = db.query(Subscription).filter(Subscription.user_id == progress.user_id).first()
            if not user or not sub or sub.status != SubscriptionStatus.ACTIVE:
                continue
            days_since = (datetime.utcnow() - sub.created_at).days if sub.created_at else 0
            lang = user.language if user.language in ONBOARDING_EMAILS else "en"
            emails = ONBOARDING_EMAILS[lang]
            for step, delay in enumerate(ONBOARDING_DELAY_DAYS):
                if step <= progress.last_email_step and step > 0:
                    continue
                if days_since < delay:
                    break
                if step <= progress.last_email_step:
                    continue
                email_cfg = emails[step]
                subject = email_cfg["subject"]
                body = email_cfg["body"](user.full_name or "there", settings.FRONTEND_URL)
                ok = send_email(to_email=user.email, subject=subject, body_html=body,
                                language=lang, country=user.country or "US")
                if ok:
                    progress.last_email_step = step
                    progress.last_email_sent_at = datetime.utcnow()
                    if step == len(emails) - 1:
                        progress.completed = True
                        progress.completed_at = datetime.utcnow()
                    db.commit()
                    sent += 1
                    break
    finally:
        db.close()
    logger.info("[onboarding] Sent %d onboarding emails", sent)


def init_onboarding(user_id: str, db):
    existing = db.query(OnboardingProgress).filter(OnboardingProgress.user_id == user_id).first()
    if existing:
        existing.subscription_activated = True
        db.commit()
        return
    progress = OnboardingProgress(user_id=user_id, subscription_activated=True)
    db.add(progress)
    db.commit()
