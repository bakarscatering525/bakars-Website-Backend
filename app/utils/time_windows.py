import logging
from datetime import datetime, time, timedelta, timezone, tzinfo
from typing import Any, Dict, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Daily menu ordering window (local business time)
DAILY_MENU_START_TIME = time(hour=11, minute=0)  # 11:00 AM
DAILY_MENU_END_TIME = time(hour=21, minute=0)    # 9:00 PM
DAILY_MENU_WINDOW_LABEL = "11:00 AM to 9:00 PM"


def _fallback_aest() -> tzinfo:
    """Fixed Australian Eastern Standard Time (+10) fallback without tzdata."""
    return timezone(timedelta(hours=10), name="AEST")


def get_timezone_label(tz: tzinfo | None) -> str:
    """Human-friendly label for a tzinfo object."""
    if tz is None:
        return "UTC"
    for attr in ("key", "zone", "_name"):
        name = getattr(tz, attr, None)
        if name:
            return str(name)
    name = tz.tzname(None)
    return name or str(tz)


def get_business_timezone() -> tzinfo:
    """Return the configured business timezone, falling back safely."""
    tz_name = settings.BUSINESS_TIMEZONE or "Australia/Sydney"
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError as exc:
        logger.warning(
            "Invalid BUSINESS_TIMEZONE '%s': %s. Falling back to AEST (+10).",
            tz_name,
            exc,
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning(
            "Failed to load BUSINESS_TIMEZONE '%s': %s. Falling back to AEST (+10).",
            tz_name,
            exc,
        )

    # Fallback to fixed AEST to align with business requirement
    try:
        return _fallback_aest()
    except Exception:
        pass

    # Ultimate fallback: system local, then UTC
    try:
        local_tz = datetime.now().astimezone().tzinfo
        if local_tz:
            return local_tz
    except Exception:
        pass

    logger.warning("Using UTC as timezone fallback for daily menu window.")
    return timezone.utc


def get_business_now() -> datetime:
    """Current datetime in the business timezone."""
    return datetime.now(get_business_timezone())


def _compute_daily_window(now: datetime) -> Tuple[datetime, datetime, timedelta]:
    """
    Compute the active daily menu window (start, end) anchored around `now`.

    The window crosses midnight, opening at 23:00 and closing at 21:00 the next day.
    """
    tz = now.tzinfo or get_business_timezone()
    crosses_midnight = DAILY_MENU_END_TIME <= DAILY_MENU_START_TIME

    if crosses_midnight:
        if now.time() < DAILY_MENU_START_TIME:
            start_date = now.date() - timedelta(days=1)
            end_date = now.date()
        else:
            start_date = now.date()
            end_date = now.date() + timedelta(days=1)
    else:
        start_date = now.date()
        end_date = now.date()

    start_dt = datetime.combine(start_date, DAILY_MENU_START_TIME, tzinfo=tz)
    end_dt = datetime.combine(end_date, DAILY_MENU_END_TIME, tzinfo=tz)
    duration = end_dt - start_dt
    return start_dt, end_dt, duration


def _format_time(dt: datetime) -> str:
    """Format time as human-readable string without leading zero."""
    formatted = dt.strftime("%I:%M %p")
    return formatted.lstrip("0") if formatted.startswith("0") else formatted


def get_daily_menu_status(now: datetime | None = None) -> Dict[str, Any]:
    """Return structured status for the daily menu ordering window."""
    current_time = now or get_business_now()
    window_start, window_end, window_span = _compute_daily_window(current_time)

    is_open = window_start <= current_time <= window_end
    tz_label = get_timezone_label(current_time.tzinfo)

    if is_open:
        next_open = window_start
        closes_at = window_end
    else:
        if current_time < window_start:
            next_open = window_start
        else:
            # After today's window closes, the next window starts the following day.
            next_open = window_start + timedelta(days=1)

        closes_at = next_open + window_span

    status: Dict[str, Any] = {
        "is_open": is_open,
        "window_label": DAILY_MENU_WINDOW_LABEL,
        "timezone": tz_label,
        "current_time": current_time,
        "opens_at": next_open,
        "closes_at": closes_at,
    }

    if not is_open:
        status["message"] = (
            f"Daily Menu orders are available from {DAILY_MENU_WINDOW_LABEL} "
            f"({tz_label}). We will reopen at {_format_time(next_open)} {tz_label}."
        )
    else:
        status["message"] = (
            f"Daily Menu orders are currently open until {_format_time(window_end)} "
            f"({tz_label})."
        )

    return status


def require_daily_menu_open(now: datetime | None = None) -> Dict[str, Any]:
    """
    Ensure the daily menu ordering window is open.

    Raises:
        ValueError: if ordering is closed.
    """
    status = get_daily_menu_status(now)
    if not status["is_open"]:
        raise ValueError(status["message"])
    return status
