import sqlite3
from . import vulnerable, secure
from labs.support import outcome

def database():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders (owner TEXT, item TEXT)")
    db.executemany("INSERT INTO orders VALUES (?, ?)", [("alice", "notebook"), ("bob", "private synthetic item")])
    return db

def demonstrate(work):
    db = database()
    try:
        payload = "alice' OR '1'='1"
        stolen = vulnerable.search(db, payload)
        fixed = secure.search(db, payload)
        normal = secure.search(db, "alice")
        return outcome(len(stolen) == 2, fixed == [], len(normal) == 1 and normal[0][0] == "alice",
                       {"payload": payload, "vulnerable_rows": stolen, "secure_rows": fixed, "normal_rows": normal})
    finally:
        db.close()
