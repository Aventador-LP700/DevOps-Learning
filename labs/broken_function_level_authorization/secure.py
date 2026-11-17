from labs.support import Denied

def deactivate(actor, target, users):
    if users.get(actor, {}).get("role") != "admin":
        raise Denied("Administrator role required")
    users[target]["active"] = False
    return True
