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
    if len(content) > 4096:
        raise Denied("Oversized dependency metadata")
    try:
        metadata = json.loads(content)
    except (ValueError, UnicodeError) as exc:
        raise Denied("Dependency metadata must be JSON") from exc
    if (not isinstance(metadata, dict) or set(metadata) != {"name", "version", "kind"}
            or metadata["kind"] != "prebuilt-metadata"
            or not isinstance(metadata["name"], str) or not metadata["name"].strip()
            or len(metadata["name"]) > 128
            or not isinstance(metadata["version"], str) or not metadata["version"].strip()
            or len(metadata["version"]) > 64):
        raise Denied("Unexpected dependency metadata")
    return metadata
