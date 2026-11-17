import json
from labs.support import Denied

def restore(payload):
    if len(payload) > 4096:
        raise Denied("Oversized preferences")
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeError, TypeError) as exc:
        raise Denied("Preferences must be JSON") from exc
    if not isinstance(data, dict) or set(data) != {"user", "theme"} or data["theme"] not in ("dark", "light") or not isinstance(data["user"], str):
        raise Denied("Invalid preferences schema")
    return data
