"""
Automated content generation pipeline.
Weekly: generate blog post + 3 LinkedIn posts per active client.
"""
import logging
from datetime import datetime
from app.database import SessionLocal
from app.models.client import Client
from app.models.subscription import Subscription, SubscriptionStatus, PlanType
from app.services.ai_service import generate_blog_post, generate_linkedin_post

logger = logging.getLogger(__name__)

CONTENT_TOPICS = {
    "real_estate": ["comment vendre son bien plus vite", "investissement locatif 2025", "erreurs à éviter en achat immobilier"],
    "restaurants": ["comment attirer plus de clients le midi", "fidéliser sa clientèle en restauration", "tendances restauration 2025"],
    "healthcare": ["communication digitale pour cabinet médical", "attirer de nouveaux patients", "gestion des avis en ligne santé"],
    "legal": ["comment un cabinet d'avocats attire des clients en ligne", "marketing digital pour avocats", "référencement local cabinet juridique"],
    "accounting": ["digitalisation cabinet comptable", "attirer des TPE/PME comme clients", "automatisation comptabilité 2025"],
    "construction": ["devis en ligne artisan", "attirer des chantiers via internet", "réputation digitale artisan"],
    "it_services": ["cloud pour PME", "cybersécurité TPE", "transformation digitale PME budget limité"],
    "coaching": ["comment trouver ses premiers clients coach", "personal branding coach", "LinkedIn pour coach professionnel"],
    "retail": ["e-commerce pour commerce local", "fidélisation client boutique", "click and collect stratégie"],
    "other": ["croissance PME 2025", "automatisation marketing local", "prospection digitale B2B"],
}


async def run_content_generation():
    logger.info("[content_pipeline] Starting weekly content generation")
    db = SessionLocal()
    try:
        # Only Growth and Pro plans get content generation
        eligible_subs = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.plan.in_([PlanType.GROWTH, PlanType.PRO]),
        ).all()

        week = datetime.utcnow().isocalendar()[1]

        for sub in eligible_subs:
            clients = db.query(Client).filter(
                Client.owner_id == sub.user_id,
                Client.is_active == True,
            ).all()

            for client in clients:
                topics = CONTENT_TOPICS.get(client.sector.value, CONTENT_TOPICS["other"])
                topic = topics[week % len(topics)]

                try:
                    blog = generate_blog_post(
                        topic=topic,
                        sector=client.sector.value,
                        keywords=client.target_keywords or [client.sector.value],
                    )
                    linkedin = generate_linkedin_post(client.business_name, client.sector.value, topic)

                    # Store in content table (simplified: log for now)
                    logger.info(
                        "[content_pipeline] client=%s blog_title=%s linkedin_len=%d",
                        client.business_name, blog.get("title", ""), len(linkedin)
                    )
                except Exception as e:
                    logger.error("[content_pipeline] client=%s error=%s", client.id, e)

    finally:
        db.close()
    logger.info("[content_pipeline] Weekly content generation completed")
