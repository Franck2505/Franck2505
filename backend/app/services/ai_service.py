import anthropic
from app.config import settings

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


# Language-specific cold email tone instructions
_EMAIL_TONE = {
    "fr": "ton professionnel et direct, vouvoiement, phrases courtes",
    "en": "professional and concise, direct value proposition",
    "es": "tono profesional y directo, ustedeo formal",
    "de": "professioneller Ton, formelle Anrede (Sie), präzise",
    "it": "tono professionale, lei formale, conciso",
    "pt": "tom profissional e direto, tratamento formal",
    "nl": "professionele toon, formele aanspreking (u), beknopt",
}

_STEP_CONTEXT = {
    "fr": {0: "premier contact", 1: "relance douce après silence", 2: "relance avec valeur ajoutée", 3: "dernier email de séparation"},
    "en": {0: "first contact", 1: "gentle follow-up after no reply", 2: "value-add follow-up", 3: "final breakup email"},
    "es": {0: "primer contacto", 1: "seguimiento suave sin respuesta", 2: "seguimiento con valor añadido", 3: "último email de cierre"},
    "de": {0: "Erstkontakt", 1: "sanfte Nachfass-Mail ohne Antwort", 2: "Nachfass mit Mehrwert", 3: "letzte Trennungs-Mail"},
    "it": {0: "primo contatto", 1: "follow-up dopo silenzio", 2: "follow-up con valore aggiunto", 3: "ultima email di chiusura"},
    "pt": {0: "primeiro contato", 1: "follow-up suave após silêncio", 2: "follow-up com valor agregado", 3: "último email de encerramento"},
    "nl": {0: "eerste contact", 1: "zachte follow-up na stilte", 2: "follow-up met toegevoegde waarde", 3: "laatste afscheids-e-mail"},
}


def generate_cold_email(
    sender_business: str,
    prospect_name: str,
    prospect_business: str,
    sector: str,
    sequence_step: int = 0,
    language: str = "fr",
) -> dict:
    tone = _EMAIL_TONE.get(language, _EMAIL_TONE["en"])
    step_ctx = _STEP_CONTEXT.get(language, _STEP_CONTEXT["en"]).get(sequence_step, "follow-up")

    prompt = f"""Write a cold B2B outreach email. Step {sequence_step + 1} ({step_ctx}).
Language: {language.upper()} — Tone: {tone}

Sender: {sender_business}
Prospect: {prospect_name or prospect_business} (sector: {sector})

Rules:
- Maximum 100 words
- No buzzwords, no fake urgency
- Personalized to their sector and cultural context
- Clear CTA (15-minute call)
- Write in {language.upper()} only
- Subject line on first line as "Subject: ..."
- Blank line then email body

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


def generate_blog_post(topic: str, sector: str, keywords: list[str], language: str = "fr") -> dict:
    kw_str = ", ".join(keywords[:5])
    prompt = f"""Write an SEO blog post in {language.upper()} for a {sector} business.

Topic: {topic}
Keywords: {kw_str}

Requirements:
- 600-800 words in {language.upper()}
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


def generate_linkedin_post(business_name: str, sector: str, topic: str, language: str = "fr") -> str:
    prompt = f"""Write a LinkedIn post in {language.upper()} for {business_name} ({sector}).
Topic: {topic}

Rules: 150-200 words, hook first line, 3-5 relevant hashtags at end. Write only the post in {language.upper()}."""

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
    high_value = ["real_estate", "legal", "accounting", "healthcare", "it_services"]
    if sector in high_value:
        score += 30
    if business_name and len(business_name) > 3:
        score += 10
    return min(score, 100.0)
