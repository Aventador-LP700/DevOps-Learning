import base64
import hashlib
import json

def accept(envelope):
    data = base64.b64decode(envelope["payload"], validate=True)
    if hashlib.sha256(data).hexdigest() != envelope["sha256"]:
        raise ValueError("Checksum mismatch")
    return json.loads(data)  # Sender also supplies checksum; origin is unauthenticated.
