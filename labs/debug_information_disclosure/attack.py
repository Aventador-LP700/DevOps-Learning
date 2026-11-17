import json
from . import vulnerable, secure
from labs.support import outcome

def fail():
    raise RuntimeError("Synthetic backend detail")
def demonstrate(work):
    _, exposed = vulnerable.handle(fail)
    status, redacted = secure.handle(fail)
    good, normal = secure.handle(lambda: "ok")
    return outcome("Traceback" in exposed["debug"] and "config" in exposed,
                   status == 500 and "Synthetic backend detail" not in json.dumps(redacted) and "config" not in redacted,
                   good == 200 and normal["result"] == "ok",
                   {"vulnerable_response": exposed, "secure_response": redacted})
