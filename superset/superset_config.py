import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "change-me-in-production-please")

SUPERSET_HOME = "/app/superset_home"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{SUPERSET_HOME}/superset.db"

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": os.getenv("REDIS_HOST", "superset_redis"),
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_DB": 1,
}
DATA_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_REDIS_DB": 2}

PREVENT_UNSAFE_DB_CONNECTIONS = False
