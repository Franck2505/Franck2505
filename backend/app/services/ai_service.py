import anthropic
from app.config import settings

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def generate_cold_email(
    sender_business: str,
    prospect_name: str,
    prospect_business: str,
    sector: str,
    sequence_step: int = 0,
) -> dict:
    step_context = {
        0: "first contact, professional and concise",
        1: "gentle follow-up after no reply",
        2: "value-add follow-up with a specific insight",
        3: "final breakup email",
    }
    context = step_context.get(sequence_step, "follow-up")

    prompt = f"""Write a cold email for B2B outreach. This is step {sequence_step + 1} ({context}).

Sender: {sender_business}
Prospect: {prospect_name or prospect_business} ({sector} sector)

Rules:
- Maximum 120 words
- No buzzwords, no fake urgency
- Personalized to their sector
- Clear CTA (15-minute call)
- Natural, human tone
- Subject line on first line prefixed with "Subject: "
- Then blank line
- Then email body

Write only the email, nothing else."""

    message = get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    lines = text.split("\n", 2)
    subject = lines[0].replace("Subject:", "").strip() if lines else "Quick question"
    body = "\n".join(lines[2:]).strip() if len(lines) > 2 else text

    return {"subject": subject, "body": body}


def generate_blog_post(topic: str, sector: str, keywords: list[str]) -> dict:
    kw_str = ", ".join(keywords[:5])
    prompt = f"""Write an SEO blog post for a {sector} business.

Topic: {topic}
Keywords to include: {kw_str}

Requirements:
- 600-800 words
- H1 title at top
- 3 H2 sections
- Practical advice, no fluff
- Naturally integrate keywords
- End with CTA

Return JSON: {{"title": "...", "content": "...", "meta_description": "..."}}"""

    message = get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    try:
        return json.loads(message.content[0].text)
    except Exception:
        return {"title": topic, "content": message.content[0].text, "meta_description": ""}


def generate_linkedin_post(business_name: str, sector: str, topic: str) -> str:
    prompt = f"""Write a LinkedIn post for {business_name} ({sector}).
Topic: {topic}

Rules: 150-200 words, hook in first line, 3-5 relevant hashtags at end.
Write only the post."""

    message = get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def score_lead(business_name: str, sector: str, has_website: bool, has_email: bool) -> float:
    score = 0.0
    if has_email:
        score += 40
    if has_website:
        score += 20
    high_value_sectors = ["real_estate", "legal", "accounting", "healthcare", "it_services"]
    if sector in high_value_sectors:
        score += 30
    if business_name and len(business_name) > 3:
        score += 10
    return min(score, 100.0)
