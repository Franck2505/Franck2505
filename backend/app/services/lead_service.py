import httpx
import asyncio
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models.lead import Lead, LeadSource, LeadStatus
from app.models.client import Client
from app.services.ai_service import score_lead
from app.i18n.locales import get_country_config, COUNTRY_CONFIG


async def scrape_google_maps(keyword: str, location: str, language: str = "fr", limit: int = 20) -> List[Dict]:
    results = []
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"{keyword} in {location}"

    async with httpx.AsyncClient(timeout=15) as client:
        params = {
            "query": query,
            "key": settings.GOOGLE_PLACES_API_KEY,
            "language": language,
        }
        resp = await client.get(url, params=params)
        data = resp.json()

        for place in data.get("results", [])[:limit]:
            results.append({
                "business_name": place.get("name"),
                "address": place.get("formatted_address"),
                "website": place.get("website", ""),
                "phone": place.get("formatted_phone_number", ""),
                "source": LeadSource.GOOGLE_MAPS,
            })

        next_token = data.get("next_page_token")
        if next_token and len(results) < limit:
            await asyncio.sleep(2)
            params2 = dict(params)
            params2["pagetoken"] = next_token
            resp2 = await client.get(url, params=params2)
            for place in resp2.json().get("results", [])[:limit - len(results)]:
                results.append({
                    "business_name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "website": place.get("website", ""),
                    "phone": place.get("formatted_phone_number", ""),
                    "source": LeadSource.GOOGLE_MAPS,
                })

    return results


async def find_email_for_domain(domain: str) -> Optional[str]:
    if not domain or not settings.HUNTER_IO_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.hunter.io/v2/domain-search",
                params={"domain": domain, "api_key": settings.HUNTER_IO_API_KEY, "limit": 1},
            )
            emails = resp.json().get("data", {}).get("emails", [])
            if emails:
                return emails[0].get("value")
    except Exception:
        pass
    return None


def extract_domain(url: str) -> Optional[str]:
    if not url:
        return None
    return url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]


def _get_location_query(country: str, base_location: Optional[str]) -> str:
    """Build a location-aware query string for Google Maps."""
    config = get_country_config(country)
    country_name = config["name"]
    if base_location and base_location.lower() not in ["france", "world", country_name.lower()]:
        return f"{base_location}, {country_name}"
    return country_name


async def generate_leads_for_client(client: Client, db: Session, max_leads: int = 50) -> int:
    created = 0
    country = client.country or "FR"
    language = client.language or "fr"
    location = _get_location_query(country, client.target_location)
    keywords = client.target_keywords or [client.sector.value.replace("_", " ")]

    for keyword in keywords[:3]:
        raw = await scrape_google_maps(
            keyword=keyword,
            location=location,
            language=language,
            limit=max_leads // max(len(keywords[:3]), 1),
        )

        for item in raw:
            existing = db.query(Lead).filter(
                Lead.client_id == client.id,
                Lead.business_name == item["business_name"],
            ).first()
            if existing:
                continue

            email = None
            domain = extract_domain(item.get("website", ""))
            if domain:
                email = await find_email_for_domain(domain)

            lead = Lead(
                client_id=client.id,
                business_name=item["business_name"],
                email=email,
                phone=item.get("phone"),
                website=item.get("website"),
                address=item.get("address"),
                source=LeadSource.GOOGLE_MAPS,
                status=LeadStatus.NEW,
                is_email_verified=bool(email),
                score=score_lead(
                    item["business_name"],
                    client.sector.value,
                    has_website=bool(item.get("website")),
                    has_email=bool(email),
                ),
            )
            db.add(lead)
            created += 1

        db.commit()

    return created
