from labs.support import Denied

def update_profile(profile, payload):
    if not isinstance(payload, dict) or set(payload) - {"display_name"}:
        raise Denied("Only display_name can be updated")
    if "display_name" in payload and (not isinstance(payload["display_name"], str) or len(payload["display_name"]) > 80):
        raise Denied("Invalid display name")
    profile.update(payload)
    return dict(profile)
