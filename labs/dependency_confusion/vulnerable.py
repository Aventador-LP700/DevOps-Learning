from labs.support import lab_fetch

def resolve(registry, name):
    candidates = [lab_fetch(registry + f"/{namespace}/{name}", {registry}) for namespace in ("private", "public")]
    return max(candidates, key=lambda package: tuple(int(x) for x in package["version"].split(".")))
