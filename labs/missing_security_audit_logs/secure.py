from datetime import datetime, timezone
import json
import secrets


def change_role(actor, target, role, users, log_path):
    allowed = users.get(actor, {}).get("role") == "admin" and target in users and role in ("user", "admin")
    event = {"timestamp": datetime.now(timezone.utc).isoformat(), "request_id": secrets.token_hex(8),
             "action": "role_change", "actor": actor, "target": target,
             "result": "allowed" if allowed else "denied"}
    # A failed log write prevents this critical action from taking place.
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event) + "\n")
    if allowed:
        users[target]["role"] = role
    return allowed
