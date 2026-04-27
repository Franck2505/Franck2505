"""
Create Stripe products and prices automatically.
Run once: python scripts/setup_stripe.py
Outputs the price IDs to paste in .env
"""
import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

if not stripe.api_key:
    print("Set STRIPE_SECRET_KEY environment variable first")
    exit(1)

PLANS = [
    {"name": "AutoGrowth Pro — Starter", "amount": 29900, "env_key": "STRIPE_PRICE_STARTER"},
    {"name": "AutoGrowth Pro — Growth",  "amount": 59900, "env_key": "STRIPE_PRICE_GROWTH"},
    {"name": "AutoGrowth Pro — Pro",     "amount": 99900, "env_key": "STRIPE_PRICE_PRO"},
]

print("Creating Stripe products and prices...\n")

for plan in PLANS:
    product = stripe.Product.create(name=plan["name"])
    price = stripe.Price.create(
        product=product.id,
        unit_amount=plan["amount"],  # cents
        currency="eur",
        recurring={"interval": "month"},
    )
    print(f"{plan['env_key']}={price.id}")

print("\n✅ Copy the above values to your .env file")
