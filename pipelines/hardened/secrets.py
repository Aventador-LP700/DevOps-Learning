"""Do not log credentials; log operation outcomes."""
import os
if not os.environ.get("LAB_TOKEN"):
    raise SystemExit("Missing credential")
print("Credential supplied; authentication step configured")
