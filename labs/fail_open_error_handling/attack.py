from . import vulnerable, secure
from labs.support import outcome

def unavailable(actor, resource):
    raise TimeoutError("Synthetic policy backend outage")

def demonstrate(work):
    exposed = vulnerable.authorize("alice", "admin-report", unavailable)
    denied = not secure.authorize("alice", "admin-report", unavailable)
    good = secure.authorize("alice", "own-order", lambda actor, resource: resource == "own-order")
    ordinary_deny = not secure.authorize("alice", "admin-report", lambda actor, resource: False)
    return outcome(exposed, denied and ordinary_deny, good,
                   {"injected_fault": "TimeoutError", "vulnerable_allowed": exposed, "secure_allowed": not denied, "healthy_allow_and_deny_preserved": good and ordinary_deny})
