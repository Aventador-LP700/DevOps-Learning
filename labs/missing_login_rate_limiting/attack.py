from . import vulnerable, secure
from labs.support import outcome

def demonstrate(work):
    a, b = vulnerable.LoginService(), secure.LoginService()
    bad = [a.login("alice", "dummy-wrong")[0] for _ in range(6)]
    guarded = [b.login("alice", "dummy-wrong")[0] for _ in range(6)]
    normal = secure.LoginService().login("alice", "dummy-correct-horse")
    return outcome(all(code == 401 for code in bad), guarded == [401,401,401,429,429,429], normal == (200, True),
                   {"attempt_count": 6, "vulnerable_statuses": bad, "secure_statuses": guarded, "scope": "In-process per-account limiter; production requires distributed state and broader abuse controls"})
