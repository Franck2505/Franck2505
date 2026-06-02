"""
Multilingual email template system.
All transactional emails in 7 languages with legal compliance footers.
"""

UNSUBSCRIBE_TEXTS = {
    "fr": "Se désinscrire",
    "en": "Unsubscribe",
    "es": "Darse de baja",
    "de": "Abmelden",
    "it": "Cancella iscrizione",
    "pt": "Cancelar inscrição",
    "nl": "Afmelden",
}

GDPR_FOOTERS = {
    "fr": "Vous recevez cet email car vos coordonnées sont publiquement disponibles. Conformément au RGPD, vous pouvez vous désinscrire à tout moment.",
    "en": "You are receiving this email because your contact details are publicly available. In accordance with GDPR/applicable law, you can unsubscribe at any time.",
    "es": "Recibe este correo porque sus datos están disponibles públicamente. De acuerdo con el RGPD, puede darse de baja en cualquier momento.",
    "de": "Sie erhalten diese E-Mail, weil Ihre Kontaktdaten öffentlich verfügbar sind. Gemäß DSGVO können Sie sich jederzeit abmelden.",
    "it": "Ricevi questa email perché i tuoi dati sono pubblicamente disponibili. Ai sensi del GDPR, puoi disiscriverti in qualsiasi momento.",
    "pt": "Você recebe este e-mail porque seus dados estão disponíveis publicamente. De acordo com o LGPD/GDPR, você pode cancelar a inscrição a qualquer momento.",
    "nl": "U ontvangt deze e-mail omdat uw contactgegevens openbaar beschikbaar zijn. U kunt zich op elk moment afmelden conform de AVG.",
}

WELCOME_SUBJECTS = {
    "fr": "Bienvenue sur AutoGrowth Pro — votre croissance commence maintenant",
    "en": "Welcome to AutoGrowth Pro — your growth starts now",
    "es": "Bienvenido a AutoGrowth Pro — tu crecimiento comienza ahora",
    "de": "Willkommen bei AutoGrowth Pro — Ihr Wachstum beginnt jetzt",
    "it": "Benvenuto su AutoGrowth Pro — la tua crescita inizia ora",
    "pt": "Bem-vindo ao AutoGrowth Pro — seu crescimento começa agora",
    "nl": "Welkom bij AutoGrowth Pro — uw groei begint nu",
}

WELCOME_BODIES = {
    "fr": lambda name, plan, url: f"""
        <h2>Bienvenue sur AutoGrowth Pro, {name} !</h2>
        <p>Votre plan <strong>{plan.upper()}</strong> est actif. Votre machine de croissance est prête.</p>
        <p>Prochaines étapes :</p>
        <ol>
            <li>Créez votre premier client dans le dashboard</li>
            <li>Lancez votre première campagne de prospection</li>
            <li>Regardez les leads arriver automatiquement</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Accéder au Dashboard →</a></p>
    """,
    "en": lambda name, plan, url: f"""
        <h2>Welcome to AutoGrowth Pro, {name}!</h2>
        <p>Your <strong>{plan.upper()}</strong> plan is now active. Your growth machine is ready.</p>
        <p>Next steps:</p>
        <ol>
            <li>Create your first client in the dashboard</li>
            <li>Launch your first outreach campaign</li>
            <li>Watch leads arrive automatically</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Go to Dashboard →</a></p>
    """,
    "es": lambda name, plan, url: f"""
        <h2>¡Bienvenido a AutoGrowth Pro, {name}!</h2>
        <p>Tu plan <strong>{plan.upper()}</strong> está activo. Tu máquina de crecimiento está lista.</p>
        <ol>
            <li>Crea tu primer cliente en el dashboard</li>
            <li>Lanza tu primera campaña de prospección</li>
            <li>Observa cómo llegan los leads automáticamente</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Ir al Dashboard →</a></p>
    """,
    "de": lambda name, plan, url: f"""
        <h2>Willkommen bei AutoGrowth Pro, {name}!</h2>
        <p>Ihr <strong>{plan.upper()}</strong>-Plan ist aktiv. Ihre Wachstumsmaschine ist bereit.</p>
        <ol>
            <li>Erstellen Sie Ihren ersten Kunden im Dashboard</li>
            <li>Starten Sie Ihre erste Akquise-Kampagne</li>
            <li>Beobachten Sie, wie Leads automatisch eintreffen</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Zum Dashboard →</a></p>
    """,
    "it": lambda name, plan, url: f"""
        <h2>Benvenuto su AutoGrowth Pro, {name}!</h2>
        <p>Il tuo piano <strong>{plan.upper()}</strong> è attivo. La tua macchina di crescita è pronta.</p>
        <ol>
            <li>Crea il tuo primo cliente nella dashboard</li>
            <li>Lancia la tua prima campagna di prospecting</li>
            <li>Guarda i lead arrivare automaticamente</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Vai alla Dashboard →</a></p>
    """,
    "pt": lambda name, plan, url: f"""
        <h2>Bem-vindo ao AutoGrowth Pro, {name}!</h2>
        <p>Seu plano <strong>{plan.upper()}</strong> está ativo. Sua máquina de crescimento está pronta.</p>
        <ol>
            <li>Crie seu primeiro cliente no dashboard</li>
            <li>Lance sua primeira campanha de prospecção</li>
            <li>Veja os leads chegando automaticamente</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Ir ao Dashboard →</a></p>
    """,
    "nl": lambda name, plan, url: f"""
        <h2>Welkom bij AutoGrowth Pro, {name}!</h2>
        <p>Uw <strong>{plan.upper()}</strong>-plan is actief. Uw groeimotor is klaar.</p>
        <ol>
            <li>Maak uw eerste klant aan in het dashboard</li>
            <li>Start uw eerste prospectiecampagne</li>
            <li>Zie leads automatisch binnenkomen</li>
        </ol>
        <p><a href="{url}/dashboard" style="background:#6366f1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">Naar Dashboard →</a></p>
    """,
}

MONTHLY_REPORT_SUBJECTS = {
    "fr": "Votre rapport mensuel AutoGrowth Pro — {month}",
    "en": "Your AutoGrowth Pro monthly report — {month}",
    "es": "Tu informe mensual AutoGrowth Pro — {month}",
    "de": "Ihr monatlicher AutoGrowth Pro Bericht — {month}",
    "it": "Il tuo report mensile AutoGrowth Pro — {month}",
    "pt": "Seu relatório mensal AutoGrowth Pro — {month}",
    "nl": "Uw maandelijks AutoGrowth Pro rapport — {month}",
}

PAYMENT_FAILED_SUBJECTS = {
    "fr": "Action requise — Paiement échoué AutoGrowth Pro",
    "en": "Action required — AutoGrowth Pro payment failed",
    "es": "Acción requerida — Pago fallido en AutoGrowth Pro",
    "de": "Handlung erforderlich — Zahlung fehlgeschlagen AutoGrowth Pro",
    "it": "Azione richiesta — Pagamento fallito AutoGrowth Pro",
    "pt": "Ação necessária — Pagamento falhou AutoGrowth Pro",
    "nl": "Actie vereist — Betaling mislukt AutoGrowth Pro",
}


def get_unsubscribe_text(lang: str) -> str:
    return UNSUBSCRIBE_TEXTS.get(lang, UNSUBSCRIBE_TEXTS["en"])


def get_compliance_footer(lang: str) -> str:
    return GDPR_FOOTERS.get(lang, GDPR_FOOTERS["en"])


def get_welcome_email(lang: str, name: str, plan: str, frontend_url: str) -> dict:
    subject = WELCOME_SUBJECTS.get(lang, WELCOME_SUBJECTS["en"])
    body_fn = WELCOME_BODIES.get(lang, WELCOME_BODIES["en"])
    return {"subject": subject, "body": body_fn(name, plan, frontend_url)}


def get_monthly_report_subject(lang: str, month: str) -> str:
    tmpl = MONTHLY_REPORT_SUBJECTS.get(lang, MONTHLY_REPORT_SUBJECTS["en"])
    return tmpl.format(month=month)


def get_payment_failed_subject(lang: str) -> str:
    return PAYMENT_FAILED_SUBJECTS.get(lang, PAYMENT_FAILED_SUBJECTS["en"])
