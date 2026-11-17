import hashlib

def store(password):
    return hashlib.md5(password.encode(), usedforsecurity=False).hexdigest()
def verify(password, stored):
    return store(password) == stored
