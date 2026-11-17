"""INTENTIONALLY VULNERABLE: run only through the isolated lab."""
import os
import subprocess
subprocess.run("printf '%s\n' " + os.environ["CHANGE_TITLE"], shell=True, check=True)
