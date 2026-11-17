from . import vulnerable, secure
from labs.support import outcome, rejected

def demonstrate(work):
    payload = "demo; printf LAB_RCE > rce-proof; #"
    result = vulnerable.diagnostic(payload, work)
    marker = work / "rce-proof"
    ran = result.returncode == 0 and marker.read_text() == "LAB_RCE"
    marker.unlink()
    blocked = rejected(lambda: secure.diagnostic(payload, work)) and not marker.exists()
    good = secure.diagnostic("demo", work)
    return outcome(ran, blocked, good.returncode == 0 and good.stdout.strip() == "demo",
                   {"payload": payload, "vulnerable_command_marker": ran, "secure_marker_exists": marker.exists(), "effect": "Temporary local file only; no network or persistence"})
