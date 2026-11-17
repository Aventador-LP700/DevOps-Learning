import os
import subprocess
import sys

def build(dependency_script, work):
    # Unsafe build hook: executes the dependency's Python source during a build.
    return subprocess.run([sys.executable, str(dependency_script)], cwd=work,
                          env={"PATH": os.defpath}, capture_output=True, text=True, timeout=3).returncode
