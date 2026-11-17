import os
import subprocess

def diagnostic(label, work):
    return subprocess.run("printf '%s\n' " + label, shell=True, cwd=work,
                          env={"PATH": os.defpath}, capture_output=True, text=True, timeout=3)
