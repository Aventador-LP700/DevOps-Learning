ALLOWED_ORIGINS = frozenset({"http://127.0.0.1:8082"})

def cors_headers(origin):
    if origin not in ALLOWED_ORIGINS:
        return {"Vary": "Origin"}
    return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
