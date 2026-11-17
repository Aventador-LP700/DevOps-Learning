import os
import re
import subprocess
from labs.support import Denied

def diagnostic(label, work):
    if not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,40}", label):
        raise Denied("Unsupported diagnostic label")
    return subprocess.run(["printf", "%s\n", label], cwd=work,
                          env={"PATH": os.defpath}, capture_output=True, text=True, timeout=3)
