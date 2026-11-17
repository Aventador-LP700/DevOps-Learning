from . import vulnerable, secure
from labs.support import outcome

def demonstrate(work):
    attacker = "http://127.0.0.1:9999"
    a, b = vulnerable.cors_headers(attacker), secure.cors_headers(attacker)
    good = secure.cors_headers("http://127.0.0.1:8082")
    return outcome(a.get("Access-Control-Allow-Origin") == attacker and a.get("Access-Control-Allow-Credentials") == "true",
                   "Access-Control-Allow-Origin" not in b, good.get("Access-Control-Allow-Origin") == "http://127.0.0.1:8082",
                   {"untrusted_origin": attacker, "vulnerable_headers": a, "secure_headers": b, "browser_validation": "See tests/browser_labs.py for real browser enforcement"})
