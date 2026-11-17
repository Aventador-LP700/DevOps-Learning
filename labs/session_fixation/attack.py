from . import vulnerable, secure
from labs.support import outcome

def demonstrate(work):
    a, b = vulnerable.SessionStore(), secure.SessionStore()
    known_a, known_b = a.start(), b.start()
    # Authentication itself is assumed complete; this tests its session transition.
    logged_a, logged_b = a.login(known_a, "alice"), b.login(known_b, "alice")
    stolen = a.user(known_a) == "alice"
    blocked = b.user(known_b) is None and logged_b != known_b
    return outcome(stolen and logged_a == known_a, blocked, b.user(logged_b) == "alice",
                   {"vulnerable_identifier_retained": logged_a == known_a, "secure_identifier_rotated": logged_b != known_b, "secure_old_session_invalidated": b.user(known_b) is None})
