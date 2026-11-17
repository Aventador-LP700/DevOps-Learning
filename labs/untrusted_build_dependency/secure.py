import hashlib
import json
from labs.support import Denied

def build(metadata_path, trusted_digest):
    # This lab consumes prebuilt dependency metadata; it never executes build hooks.
    if metadata_path.suffix != ".json":
        raise Denied("Source build hooks are disabled")
    content = metadata_path.read_bytes()
    if hashlib.sha256(content).hexdigest() != trusted_digest:
        raise Denied("Prebuilt metadata digest mismatch")
    metadata = json.loads(content)
    if set(metadata) != {"name", "version", "kind"} or metadata["kind"] != "prebuilt-metadata":
        raise Denied("Unexpected dependency metadata")
    return metadata
