"""Export the two known reports without mounting the host into the attack container."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
container = subprocess.check_output(
    ["docker", "compose", "run", "--detach", "--no-deps", "--entrypoint", "python", "lab", "-c", "import time; time.sleep(120)"],
    cwd=root, text=True,
).strip()
try:
    destination = root / "reports"
    destination.mkdir(exist_ok=True)
    for name in ("assessment.json", "assessment.md"):
        subprocess.run(["docker", "cp", f"{container}:/reports/{name}", str(destination / name)], check=True)
    print(f"Exported evidence to {destination}")
finally:
    subprocess.run(["docker", "rm", "--force", container], check=True)
