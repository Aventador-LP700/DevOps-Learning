def update_profile(profile, payload):
    profile.update(payload)
    return dict(profile)
