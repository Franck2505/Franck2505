"""
International configuration: 26 countries, 7 languages, 6 currencies, timezones.
Drives multi-language email generation, billing, lead scraping, and compliance.
"""
from typing import Optional

LANGUAGES = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
}

CURRENCIES = {
    "EUR": {"symbol": "€", "position": "after",  "countries": ["FR","DE","ES","IT","PT","NL","BE","AT","FI","IE","GR","LU"]},
    "USD": {"symbol": "$", "position": "before", "countries": ["US","MX","CO","AR"]},
    "GBP": {"symbol": "£", "position": "before", "countries": ["GB"]},
    "CAD": {"symbol": "CA$","position": "before","countries": ["CA"]},
    "AUD": {"symbol": "A$", "position": "before", "countries": ["AU"]},
    "BRL": {"symbol": "R$", "position": "before", "countries": ["BR"]},
    "CHF": {"symbol": "Fr.", "position": "before", "countries": ["CH"]},
}

# Plan prices per currency (monthly, exact values)
PLAN_PRICES: dict[str, dict[str, int]] = {
    "EUR": {"starter": 299,  "growth": 599,  "pro": 999},
    "USD": {"starter": 329,  "growth": 649,  "pro": 1099},
    "GBP": {"starter": 249,  "growth": 499,  "pro": 849},
    "CAD": {"starter": 449,  "growth": 899,  "pro": 1499},
    "AUD": {"starter": 499,  "growth": 999,  "pro": 1699},
    "BRL": {"starter": 1690, "growth": 3390, "pro": 5690},
    "CHF": {"starter": 299,  "growth": 599,  "pro": 999},
}

# Country metadata
COUNTRY_CONFIG: dict[str, dict] = {
    "FR": {"name": "France",         "language": "fr", "currency": "EUR", "timezone": "Europe/Paris",     "compliance": "gdpr"},
    "BE": {"name": "Belgique",       "language": "fr", "currency": "EUR", "timezone": "Europe/Brussels",  "compliance": "gdpr"},
    "CH": {"name": "Suisse",         "language": "fr", "currency": "CHF", "timezone": "Europe/Zurich",    "compliance": "gdpr"},
    "LU": {"name": "Luxembourg",     "language": "fr", "currency": "EUR", "timezone": "Europe/Luxembourg","compliance": "gdpr"},
    "DE": {"name": "Deutschland",    "language": "de", "currency": "EUR", "timezone": "Europe/Berlin",    "compliance": "gdpr"},
    "AT": {"name": "Österreich",     "language": "de", "currency": "EUR", "timezone": "Europe/Vienna",    "compliance": "gdpr"},
    "ES": {"name": "España",         "language": "es", "currency": "EUR", "timezone": "Europe/Madrid",    "compliance": "gdpr"},
    "MX": {"name": "México",         "language": "es", "currency": "USD", "timezone": "America/Mexico_City","compliance": "none"},
    "CO": {"name": "Colombia",       "language": "es", "currency": "USD", "timezone": "America/Bogota",   "compliance": "none"},
    "AR": {"name": "Argentina",      "language": "es", "currency": "USD", "timezone": "America/Argentina/Buenos_Aires","compliance": "none"},
    "IT": {"name": "Italia",         "language": "it", "currency": "EUR", "timezone": "Europe/Rome",      "compliance": "gdpr"},
    "PT": {"name": "Portugal",       "language": "pt", "currency": "EUR", "timezone": "Europe/Lisbon",    "compliance": "gdpr"},
    "BR": {"name": "Brasil",         "language": "pt", "currency": "BRL", "timezone": "America/Sao_Paulo","compliance": "lgpd"},
    "NL": {"name": "Nederland",      "language": "nl", "currency": "EUR", "timezone": "Europe/Amsterdam", "compliance": "gdpr"},
    "GB": {"name": "United Kingdom", "language": "en", "currency": "GBP", "timezone": "Europe/London",    "compliance": "uk_gdpr"},
    "US": {"name": "United States",  "language": "en", "currency": "USD", "timezone": "America/New_York", "compliance": "can_spam"},
    "CA": {"name": "Canada",         "language": "en", "currency": "CAD", "timezone": "America/Toronto",  "compliance": "casl"},
    "AU": {"name": "Australia",      "language": "en", "currency": "AUD", "timezone": "Australia/Sydney", "compliance": "spam_act"},
    "IE": {"name": "Ireland",        "language": "en", "currency": "EUR", "timezone": "Europe/Dublin",    "compliance": "gdpr"},
    "FI": {"name": "Suomi",          "language": "en", "currency": "EUR", "timezone": "Europe/Helsinki",  "compliance": "gdpr"},
    "GR": {"name": "Ελλάδα",         "language": "en", "currency": "EUR", "timezone": "Europe/Athens",    "compliance": "gdpr"},
    "SG": {"name": "Singapore",      "language": "en", "currency": "USD", "timezone": "Asia/Singapore",   "compliance": "pdpa"},
    "AE": {"name": "UAE",            "language": "en", "currency": "USD", "timezone": "Asia/Dubai",       "compliance": "none"},
    "ZA": {"name": "South Africa",   "language": "en", "currency": "USD", "timezone": "Africa/Johannesburg","compliance": "popia"},
    "IN": {"name": "India",          "language": "en", "currency": "USD", "timezone": "Asia/Kolkata",     "compliance": "none"},
    "JP": {"name": "Japan",          "language": "en", "currency": "USD", "timezone": "Asia/Tokyo",       "compliance": "appi"},
}

# Optimal email send windows per timezone (local time, avoid weekends)
OPTIMAL_SEND_HOURS = {
    "morning":   {"start": 8,  "end": 10},
    "lunchtime": {"start": 12, "end": 13},
    "afternoon": {"start": 14, "end": 16},
}

# Compliance rules per type
COMPLIANCE_RULES = {
    "gdpr":     {"unsubscribe_required": True,  "consent_required": True,  "physical_address": True,  "opt_out_days": 10},
    "uk_gdpr":  {"unsubscribe_required": True,  "consent_required": True,  "physical_address": True,  "opt_out_days": 10},
    "can_spam": {"unsubscribe_required": True,  "consent_required": False, "physical_address": True,  "opt_out_days": 10},
    "casl":     {"unsubscribe_required": True,  "consent_required": True,  "physical_address": True,  "opt_out_days": 10},
    "lgpd":     {"unsubscribe_required": True,  "consent_required": True,  "physical_address": True,  "opt_out_days": 15},
    "spam_act": {"unsubscribe_required": True,  "consent_required": False, "physical_address": True,  "opt_out_days": 5},
    "pdpa":     {"unsubscribe_required": True,  "consent_required": True,  "physical_address": False, "opt_out_days": 10},
    "popia":    {"unsubscribe_required": True,  "consent_required": True,  "physical_address": True,  "opt_out_days": 10},
    "appi":     {"unsubscribe_required": True,  "consent_required": True,  "physical_address": False, "opt_out_days": 10},
    "none":     {"unsubscribe_required": True,  "consent_required": False, "physical_address": False, "opt_out_days": 10},
}


def get_country_config(country_code: str) -> dict:
    return COUNTRY_CONFIG.get(country_code.upper(), COUNTRY_CONFIG["US"])


def get_currency_for_country(country_code: str) -> str:
    config = get_country_config(country_code)
    return config["currency"]


def get_language_for_country(country_code: str) -> str:
    config = get_country_config(country_code)
    return config["language"]


def get_plan_price(plan: str, currency: str) -> int:
    prices = PLAN_PRICES.get(currency, PLAN_PRICES["EUR"])
    return prices.get(plan, PLAN_PRICES["EUR"][plan])


def format_price(amount: int, currency: str) -> str:
    cfg = CURRENCIES.get(currency, CURRENCIES["EUR"])
    if cfg["position"] == "before":
        return f"{cfg['symbol']}{amount:,}"
    return f"{amount:,} {cfg['symbol']}"


def get_compliance(country_code: str) -> dict:
    config = get_country_config(country_code)
    return COMPLIANCE_RULES.get(config["compliance"], COMPLIANCE_RULES["none"])


def detect_country_from_ip(ip: str) -> str:
    """Placeholder — in production use ip2country or MaxMind GeoIP."""
    return "FR"
