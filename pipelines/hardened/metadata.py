"""Treat contribution metadata as data; never interpolate it into shell code."""
import os
import subprocess
subprocess.run(["printf", "%s\n", os.environ["CHANGE_TITLE"]], check=True)
