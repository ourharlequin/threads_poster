"""
Конфигурация reddit_trends: сабреддиты и маппинг аккаунтов → группа + язык.
Добавляй новые аккаунты сюда при расширении на Slava, Budimir и т.д.
"""

SUBREDDITS: dict[str, list[str]] = {
    "startup": [
#        "startups",
        "founder",
        "startup",
        "TechStartups",
        "Entrepreneur",
        "StartupFuture",
    ],
    "remote_work": [
        "WorkFromHome",
        "wfh",
        "productivity",
        "procrastination",
        "digitalnomad",
    ],
    "30s": [
        "midlifecrisis",
        "Adulting",
        "millenials",
        "AskMenOver30",
    ],
    "20s_student": [
        "twentyagers",
        "twenties",
        "youngentrepreneur",
    ],
    "cycling": [
        "cycling",
        "bicycling",
        "bicycletouring",
        "bikecommuting",
    ],
    "claude": [
        "claude",
        "ClaudeAI",
        "ClaudeCode",
        "claudexplorers",
        "ClaudeHomies",
    ],
    "rio_lifestyle": [
        "riodejaneiro",
        "brasil",
        "Rio",
        "travel",
    ],
    "fashion_culture": [
        "femalefashionadvice",
        "malefashionadvice",
        "wine",
        "jewelry",
        "streetwear",
    ],
#    "nomad_life": [
#        "digitalnomad",
#        "NonDigitalNomads",
#        "travel",
#        "NomadCapitalist",
#        "longtermtravel",
#    ],
#    "devops": [
#        "devops",
#        "devopsGuru",
#        "devsecops",
#        "ExperiencedDevs",
#    ],
#    "coaching": [
#        "Coaching",
#        "personaltraining",
#        "confession",
#        "AmIOverreacting",
#        "AmItheAsshole",
#    ],
}

# account_id → группа сабреддитов + язык для перевода тем
ACCOUNTS: dict[str, dict] = {
    # Slava
    "saas.memo":           {"group": "startup",        "lang": "en"},
    "slow.routes.in.head": {"group": "remote_work",    "lang": "es"},
    "giraffe.from.mobile": {"group": "30s",            "lang": "ru"},
    "tiger.on.remote":     {"group": "20s_student",    "lang": "ru"},

    # Tanya
    "pao.e.mar":           {"group": "rio_lifestyle",  "lang": "pt"},
    "trick.trend":         {"group": "fashion_culture","lang": "en"},

    # Budimir
    "cycling_superhero":   {"group": "cycling",        "lang": "en"},
    "claude_space":        {"group": "claude",          "lang": "ru"},
}

LANG_NAMES = {
    "en": "English",
    "ru": "Russian",
    "es": "Spanish",
    "pt": "Brazilian Portuguese",
}
