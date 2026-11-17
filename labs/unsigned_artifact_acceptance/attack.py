import base64
import hashlib
import json
import secrets
from . import vulnerable, secure
from labs.support import outcome, rejected

def demonstrate(work):
    key = secrets.token_bytes(32)
    malicious = json.dumps({"app": "untrusted-publisher", "version": "99.0.0"}).encode()
    unsigned = {"payload": base64.b64encode(malicious).decode(), "sha256": hashlib.sha256(malicious).hexdigest()}
    accepted = vulnerable.accept(unsigned)
    blocked = rejected(lambda: secure.accept(unsigned, key))
    trusted = json.dumps({"app": "trusted-publisher", "version": "1.0.0"}).encode()
    authenticated = secure.authenticate(trusted, key)
    normal = secure.accept(authenticated, key)
    forged = dict(authenticated, payload=base64.b64encode(malicious).decode())
    tamper_blocked = rejected(lambda: secure.accept(forged, key))
    return outcome(accepted["app"] == "untrusted-publisher", blocked and tamper_blocked, normal["app"] == "trusted-publisher",
                   {"vulnerable_sender_checksum_accepted": True, "secure_unsigned_denied": blocked, "secure_modified_envelope_denied": tamper_blocked, "authenticator": "HMAC-SHA256 with an ephemeral shared key; this is a MAC, not a public-key digital signature", "difference_from_03": "Attacker supplies both artifact and matching checksum; trusted producer authentication is missing"})
