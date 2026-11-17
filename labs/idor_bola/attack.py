from . import vulnerable, secure
from labs.support import outcome, rejected

def demonstrate(work):
    stolen = vulnerable.read_order("alice", "200")
    blocked = rejected(lambda: secure.read_order("alice", "200"))
    own = secure.read_order("alice", "100")
    return outcome(stolen["owner"] == "bob", blocked, own["owner"] == "alice",
                   {"requested_object": "200", "attacker": "alice", "vulnerable_owner": stolen["owner"], "secure": "Ownership enforced"})
