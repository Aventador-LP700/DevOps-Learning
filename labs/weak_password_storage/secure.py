import hashlib
import hmac
import secrets

N, R, P = 16384, 8, 1

def store(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P, maxmem=64 * 1024 * 1024)
    return "scrypt$16384$8$1$" + salt.hex() + "$" + digest.hex()

def verify(password, stored):
    try:
        scheme, n, r, p, salt, expected = stored.split("$")
        # Do not allow an attacker-controlled record to select costly work factors.
        if (scheme, n, r, p) != ("scrypt", "16384", "8", "1") or len(salt) != 32 or len(expected) != 128:
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=N, r=R, p=P, maxmem=64 * 1024 * 1024)
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError, AttributeError):
        return False
