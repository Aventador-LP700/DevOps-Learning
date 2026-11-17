from . import vulnerable, secure
from labs.support import outcome, rejected

def demonstrate(work):
    a, b = {"role": "user", "display_name": "Alice"}, {"role": "user", "display_name": "Alice"}
    changed = vulnerable.update_profile(a, {"role": "admin"})
    blocked = rejected(lambda: secure.update_profile(b, {"role": "admin"})) and b["role"] == "user"
    normal = secure.update_profile(b, {"display_name": "Alice Updated"})
    return outcome(changed["role"] == "admin", blocked, normal["display_name"] == "Alice Updated",
                   {"attack_payload": {"role": "admin"}, "vulnerable_role": changed["role"], "secure_role": normal["role"]})
