from __future__ import annotations
from datetime import datetime
from homeassistant.util import dt as dt_util


def parse_datetime_utc(hass, val: str):
    """Parse a datetime string and return a timezone-aware UTC datetime.

    Attempts to parse strings using Home Assistant's ``parse_datetime`` helper
    before falling back to a manual ``strptime`` with the default
    ``"%Y-%m-%d %H:%M:%S"`` format. Any parsing or timezone failures result in
    ``None`` being returned.
    """
    if not val:
        return None
    dt_parsed = dt_util.parse_datetime(val)
    if dt_parsed is not None:
        try:
            return dt_util.as_utc(dt_parsed)
        except (ValueError, TypeError):
            return None
    try:
        dt_local = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None
    tz = dt_util.get_time_zone(getattr(getattr(hass, "config", None), "time_zone", None) or "UTC")
    if tz is not None:
        try:
            dt_local = tz.localize(dt_local)
        except Exception:
            return None
    try:
        return dt_util.as_utc(dt_local)
    except (ValueError, TypeError):
        return None
