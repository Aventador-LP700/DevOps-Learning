from labs.support import Denied

def read_file(public_dir, name):
    target = (public_dir / name).resolve()
    # Safety envelope prevents host reads; application public/private boundary is missing.
    if not target.is_relative_to(public_dir.parent.resolve()):
        raise Denied("Outside synthetic lab storage")
    return target.read_text()
