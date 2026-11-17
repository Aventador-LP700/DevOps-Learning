def authorize(actor, resource, backend):
    try:
        return backend(actor, resource) is True
    except Exception:
        return False  # Policy uncertainty cannot grant access.
