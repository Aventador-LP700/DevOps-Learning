from . import vulnerable, secure
from labs.support import outcome, rejected

from .data import fixtures

def demonstrate(work):
    public = fixtures(work)
    name = "../private/payroll.txt"
    stolen = vulnerable.read_file(public, name)
    blocked = rejected(lambda: secure.read_file(public, name))
    good = secure.read_file(public, "welcome.txt")
    return outcome(stolen == "SYNTHETIC_PRIVATE_PAYROLL", blocked, good == "Synthetic public welcome",
                   {"requested_path": name, "vulnerable_data": stolen, "secure": "Resolved path constrained to public root", "host_file_access": False})
