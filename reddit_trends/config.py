"""
Конфигурация reddit_trends: сабреддиты и маппинг аккаунтов → группа + язык.
Добавляй новые аккаунты сюда при расширении на Slava, Budimir и т.д.
"""

SUBREDDITS: dict[str, list[str]] = {
    "philosophy": [
        "philosophy",
        "askphilosophy",
        "unpopularopinion",
        "confession",
        "AmItheAsshole",
        "relationship_advice",
        "LifeProTips",
    ],
#    "corporate": [
#        "anticonsumption",
#        "collapse",
#        "worldnews",
#        "recruitinghell",
#        "jobs",
#        "AskHistorians",
#        "economics",
#    ],
    "nomad_life": [
        "digitalnomad",
#        "digitalnomadlife",
        "NonDigitalNomads",
        "travel",
        "NomadCapitalist",
        "longtermtravel",
#        "TravelHacks",
    ],
    "startup": [
#        "startups",
        "founder",
        "startup",
        "TechStartups",
        "Entrepreneur",
        "StartupFuture",
    ],
    "devops": [
        "devops",
        "devopsGuru",
        "devsecops",
        "ExperiencedDevs",
    ],
    "30s": [
        "midlifecrisis",
        "Adulting",
##        "Millennials",
        "millenials",
        "AskMenOver30",
    ],
    "20s_student": [
        "twentyagers",
        "twenties",
        "youngentrepreneur",
    ],
    "coaching": [
        "Coaching",
        "personaltraining",
        "confession",
        "AmIOverreacting",
        "AmItheAsshole",
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
}

# account_id → группа сабреддитов + язык для перевода тем
ACCOUNTS: dict[str, dict] = {
    # Tanya
    "friction.archive": {"group": "philosophy", "lang": "en"},
    "el.cuerpo.que.piensa": {"group": "philosophy", "lang": "es"},
    "nehochu_neznau": {"group": "philosophy", "lang": "ru"},

    # Slava — добавить аккаунты
    "wifi.wanderer317": {"group": "nomad_life", "lang": "en"},
    "saas.memo": {"group": "startup", "lang": "en"},
    "slow.routes.in.head": {"group": "devops", "lang": "es"},
    "giraffe.from.mobile": {"group": "30s", "lang": "ru"},
    "tiger.on.remote": {"group": "20s_student", "lang": "ru"},
    "bytededust": {"group": "coaching", "lang": "en"},

    # Budimir — добавить аккаунты
    "cycling_superhero": {"group": "cycling", "lang": "en"},
    "claude_space": {"group": "claude", "lang": "ru"},
}

LANG_NAMES = {
    "en": "English",
    "ru": "Russian",
    "es": "Spanish",
}
