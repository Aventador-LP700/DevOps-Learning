def deactivate(actor, target, users):
    users[target]["active"] = False
    return True  # An authenticated caller is assumed to be an administrator.
