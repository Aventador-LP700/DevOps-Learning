def authorize(actor, resource, backend):
    try:
        return bool(backend(actor, resource))
    except Exception:
        return True  # An unavailable policy service becomes an authorization bypass.
