from pathlib import Path
from labs.support import Denied

def read_file(public_dir, name):
    if Path(name).is_absolute():
        raise Denied("Absolute paths are not allowed")
    base = public_dir.resolve()
    target = (base / name).resolve()
    if not target.is_relative_to(base):
        raise Denied("File outside public directory")
    return target.read_text()
