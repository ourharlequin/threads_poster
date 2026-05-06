import asyncio
import os
import subprocess

WHITELIST = {"generate_posts.py", "test_publish.py", "fetch_insights.py", "refresh_tokens.py"}


def _check(script: str) -> None:
    if script not in WHITELIST:
        raise ValueError(f"Script not whitelisted: {script}")


def _env(db_path: str) -> dict:
    return {**os.environ, "DB_PATH": db_path}


async def run_async(script: str, scripts_dir: str, db_path: str, args: list[str] | None = None) -> None:
    _check(script)
    proc = await asyncio.create_subprocess_exec(
        "python", script, *(args or []),
        cwd=scripts_dir,
        env=_env(db_path),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    asyncio.ensure_future(proc.wait())


def run_sync(
    script: str,
    scripts_dir: str,
    db_path: str,
    args: list[str] | None = None,
    timeout: int = 60,
) -> tuple[int, str]:
    _check(script)
    result = subprocess.run(
        ["python", script, *(args or [])],
        cwd=scripts_dir,
        env=_env(db_path),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout + result.stderr
