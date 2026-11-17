from labs.support import lab_fetch

def fetch_preview(url, public_origin, internal_origin):
    # Intentionally misses the application egress rule; lab safety still applies.
    return lab_fetch(url, {public_origin, internal_origin})
