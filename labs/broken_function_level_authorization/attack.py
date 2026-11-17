from . import vulnerable, secure
from labs.support import outcome, rejected

def users():
    return {"alice": {"role": "user", "active": True}, "bob": {"role": "user", "active": True}, "admin": {"role": "admin", "active": True}}
def demonstrate(work):
    a, b, c = users(), users(), users()
    vulnerable.deactivate("alice", "bob", a)
    blocked = rejected(lambda: secure.deactivate("alice", "bob", b)) and b["bob"]["active"]
    allowed = secure.deactivate("admin", "bob", c) and not c["bob"]["active"]
    return outcome(not a["bob"]["active"], blocked, allowed,
                   {"vulnerable_target_active": a["bob"]["active"], "secure_target_active": b["bob"]["active"], "admin_action_allowed": allowed})
