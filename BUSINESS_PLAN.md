# AutoGrowth Pro — Business Machine €30K/mois

## Modèle économique

| Plan     | Prix    | Leads/mois | Cibles       |
|----------|---------|------------|--------------|
| Starter  | €299/mo | 100        | Solopreneurs |
| Growth   | €599/mo | 500        | PME          |
| Pro      | €999/mo | Illimités  | Agences      |

### Scénario €30K MRR

| Plan    | Clients | Revenus   |
|---------|---------|-----------|
| Pro     | 10      | €9,990    |
| Growth  | 20      | €11,980   |
| Starter | 30      | €8,970    |
| **Total** | **60** | **€30,940** |

---

## Architecture technique

```
AutoGrowth Pro
├── backend/          FastAPI + PostgreSQL + APScheduler
│   ├── Auth JWT
│   ├── Stripe billing (webhooks)
│   ├── Lead generation (Google Places + Hunter.io)
│   ├── Email automation (SMTP + tracking)
│   └── AI content (Claude API)
├── frontend/         Next.js 14 + Tailwind
│   ├── Landing page (conversion-optimized)
│   ├── Dashboard client
│   ├── Lead management
│   └── Campaign management
└── infrastructure/   Docker + Nginx + PostgreSQL + Redis
```

---

## Automatisations actives 24/7

| Job                    | Fréquence       | Description                             |
|------------------------|-----------------|-----------------------------------------|
| Génération de leads    | Chaque nuit 03h | Google Maps scraping + enrichissement   |
| Envoi emails           | Toutes 30min    | Emails IA personnalisés + relances auto |
| Contenu IA             | Hebdomadaire    | Blog posts + LinkedIn posts             |
| Rapports clients       | 1er du mois     | Stats complètes envoyées par email      |
| Vérification paiements | Quotidien 06h   | Dunning + relances impayés              |

---

## Stack APIs requises

- **Stripe** : Paiements récurrents (dashboard.stripe.com)
- **Anthropic** : Génération emails/contenu (console.anthropic.com)
- **Google Places API** : Scraping leads locaux
- **Hunter.io** : Enrichissement emails
- **SendGrid** : Envoi emails SMTP

---

## Déploiement

### Serveur recommandé
- VPS Hetzner CX31 (4vCPU, 8GB RAM) = **€15/mois**
- Domaine + SSL = **€15/an**

### Étapes
```bash
# 1. Cloner et configurer
cp .env.example .env
# Remplir toutes les clés API dans .env

# 2. Créer les produits Stripe
python scripts/setup_stripe.py

# 3. Lancer
docker compose up -d

# 4. Vérifier
curl http://localhost:8000/health
```

### Stripe webhook
Configurer l'URL : `https://autogrowth.pro/billing/webhook`
Events : `checkout.session.completed`, `invoice.payment_succeeded`,
         `invoice.payment_failed`, `customer.subscription.deleted`

---

## Funnel d'acquisition

```
Traffic (SEO + LinkedIn + Ads)
        ↓
  Landing page (autogrowth.pro)
        ↓
  Trial 14 jours gratuit
        ↓
  Conversion Stripe (~15-25%)
        ↓
  Retention (NRR > 100% via upsell)
```

### Canaux d'acquisition
1. **LinkedIn** : Posts quotidiens automatisés sur la prospection B2B
2. **SEO** : Blog généré par l'IA (articles sectoriels) → trafic organique
3. **Cold email** : La plateforme se prospecte elle-même (dogfooding)
4. **Partenariats** : Agences web, consultants marketing (commission 20%)

---

## Métriques cibles

| Métrique          | Objectif   |
|-------------------|-----------|
| MRR               | €30,000   |
| Churn mensuel     | < 5%      |
| LTV moyen         | €3,600    |
| CAC max           | €400      |
| Payback period    | < 2 mois  |
| Taux d'ouverture  | 40-50%    |
| Taux de réponse   | 6-12%     |
