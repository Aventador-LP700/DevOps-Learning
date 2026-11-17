import base64
import hashlib
import hmac
import json
from labs.support import Denied

def authenticate(data, key):
    if len(key) < 32:
        raise Denied("Use a randomly generated lab key of at least 32 bytes")
    return {"payload": base64.b64encode(data).decode(), "tag": hmac.new(key, data, hashlib.sha256).hexdigest()}

def accept(envelope, key):
    if not isinstance(envelope, dict) or set(envelope) != {"payload", "tag"} or not isinstance(envelope["tag"], str):
        raise Denied("Authenticated envelope required")
    try:
        data = base64.b64decode(envelope["payload"], validate=True)
        expected = authenticate(data, key)["tag"]
        valid = hmac.compare_digest(expected, envelope["tag"])
    except (ValueError, TypeError) as exc:
        raise Denied("Invalid artifact envelope") from exc
    if not valid:
        raise Denied("Artifact authentication failed")
    return json.loads(data)
