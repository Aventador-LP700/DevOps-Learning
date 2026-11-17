from . import vulnerable, secure
from labs.support import outcome

def demonstrate(work):
    password = "dummy-correct-horse"
    weak_a, weak_b = vulnerable.store(password), vulnerable.store(password)
    strong_a, strong_b = secure.store(password), secure.store(password)
    dictionary = {vulnerable.store(p): p for p in ("dummy-wrong", password, "dummy-other")}
    recovered = dictionary.get(weak_a) == password
    no_weak_format = not secure.verify(password, weak_a)
    normal = secure.verify(password, strong_a) and not secure.verify("dummy-wrong", strong_a)
    return outcome(recovered and weak_a == weak_b, no_weak_format and strong_a != strong_b, normal,
                   {"weak_hashes_equal": weak_a == weak_b, "tiny_dictionary_recovered_dummy": recovered, "secure_hashes_differ": strong_a != strong_b, "secure_algorithm": "scrypt n=16384,r=8,p=5 with random 16-byte salt", "limitation": "A weak password remains guessable offline; salted adaptive hashing raises cost, not password entropy"})
