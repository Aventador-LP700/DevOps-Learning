import secrets

def handle(operation):
    try:
        return 200, {"result": operation()}
    except Exception:
        # Return a correlation identifier, not exception text or configuration.
        return 500, {"error": "Request could not be completed", "request_id": secrets.token_hex(8)}
