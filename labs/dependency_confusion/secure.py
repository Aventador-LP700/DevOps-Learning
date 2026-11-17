import hashlib
from labs.support import Denied, lab_fetch

def resolve(registry, name, version, trusted_digest):
    package = lab_fetch(registry + f"/private/{name}", {registry})
    digest = hashlib.sha256(package["content"].encode()).hexdigest()
    if package["namespace"] != "private" or package["name"] != name or package["version"] != version or digest != trusted_digest:
        raise Denied("Dependency identity or pinned content mismatch")
    return package
