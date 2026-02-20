import os
import sys
from datetime import datetime, timedelta, timezone

COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


def supports_color() -> bool:
    if os.getenv("NO_COLOR"):
        return False
    if os.getenv("FORCE_COLOR"):
        return True
    return True


def colorize(text: str, color: str) -> str:
    if supports_color():
        return f"{color}{text}{COLOR_RESET}"
    return text


def log_error(message: str) -> None:
    prefix = colorize("[digital-edd-logger] ERROR:", f"{COLOR_RED}{COLOR_BOLD}")
    print(f"{prefix} {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    prefix = colorize("[digital-edd-logger] WARNING:", f"{COLOR_YELLOW}{COLOR_BOLD}")
    print(f"{prefix} {message}", file=sys.stderr)


def log_info(message: str) -> None:
    prefix = colorize("[digital-edd-logger]", COLOR_CYAN)
    print(f"{prefix} {message}")


def is_production() -> bool:
    env = os.getenv("ENV", "").lower()
    return env in {"prod", "production", "qas", "qa"}


def get_mexico_time_as_utc() -> str:
    cst = timezone(timedelta(hours=-6))
    now = datetime.now(cst)
    return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}.{int(now.microsecond / 1000):03d}Z"
