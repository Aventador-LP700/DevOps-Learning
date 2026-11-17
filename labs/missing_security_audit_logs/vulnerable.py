def change_role(actor, target, role, users, log_path):
    if users.get(actor, {}).get("role") != "admin":
        return False
    users[target]["role"] = role
    return True  # Important action silently changes state.
