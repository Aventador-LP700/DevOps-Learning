"""INTENTIONALLY VULNERABLE: logs findings but still reports success."""
import json
import os
from pathlib import Path
print(json.dumps(json.loads(Path(os.environ["SCAN_REPORT"]).read_text())))
print("Advisory scan completed. Release allowed regardless of findings.")
