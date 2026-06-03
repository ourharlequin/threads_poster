import os
from dotenv import dotenv_values

PARTICIPANTS_DIR = "/app/participants"


def _discover_participants() -> dict[str, dict]:
    result = {}
    if not os.path.isdir(PARTICIPANTS_DIR):
        return result
    for name in sorted(os.listdir(PARTICIPANTS_DIR)):
        path = os.path.join(PARTICIPANTS_DIR, name)
        if os.path.isdir(path):
            result[name] = {
                "scripts_dir": path,
                "db_path":     f"/app/data/{name}/data.duckdb",
                "env_path":    os.path.join(path, ".env"),
            }
    return result


PARTICIPANTS: dict[str, dict] = _discover_participants()
REGISTRY:     dict[str, dict] = {}


def build_registry() -> dict[str, dict]:
    result = {}
    for participant, config in PARTICIPANTS.items():
        if not os.path.exists(config["env_path"]):
            continue
        env = dotenv_values(config["env_path"])
        for i in range(1, 100):
            acc_id = env.get(f"ACCOUNT_{i}_ID")
            if not acc_id:
                break
            user_id = env.get(f"ACCOUNT_{i}_USER_ID")
            token = env.get(f"ACCOUNT_{i}_THREADS_TOKEN") or env.get("THREADS_TOKEN")
            if user_id and token:
                result[acc_id] = {
                    "account_id":  acc_id,
                    "participant": participant,
                    "user_id":     user_id,
                    "token":       token,
                    "db_path":     config["db_path"],
                    "scripts_dir": config["scripts_dir"],
                }
    return result


def get_account(account_id: str) -> dict:
    if account_id not in REGISTRY:
        raise KeyError(account_id)
    return REGISTRY[account_id]
