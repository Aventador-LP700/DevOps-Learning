import hashlib
from . import vulnerable, secure
from labs.support import json_service, outcome

def demonstrate(work):
    name = "secureforge-utils"
    trusted = {"name": name, "namespace": "private", "version": "1.0.0", "content": "trusted-local-library"}
    attacker = {"name": name, "namespace": "public", "version": "99.0.0", "content": "synthetic-attacker-library"}
    expected = hashlib.sha256(trusted["content"].encode()).hexdigest()
    with json_service({f"/private/{name}": trusted, f"/public/{name}": attacker}) as (registry, requests):
        chosen = vulnerable.resolve(registry, name)
        pinned = secure.resolve(registry, name, "1.0.0", expected)
        return outcome(chosen["namespace"] == "public", pinned["namespace"] != "public", pinned == trusted,
                       {"vulnerable_source": chosen["namespace"], "vulnerable_version": chosen["version"], "secure_source": pinned["namespace"], "registry_requests": list(requests), "simulation": "Real loopback JSON index; no PyPI traffic or package installation"})
