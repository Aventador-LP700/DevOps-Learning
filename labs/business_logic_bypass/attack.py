import sqlite3
from . import vulnerable, secure
from labs.support import outcome, rejected

def database():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE redemptions (user TEXT NOT NULL, coupon TEXT NOT NULL, PRIMARY KEY(user,coupon))")
    return db

def demonstrate(work):
    a, b = database(), database()
    try:
        first = vulnerable.checkout(a, "alice", "ONCE10")
        repeated = vulnerable.checkout(a, "alice", "ONCE10")
        original = secure.checkout(b, "alice", "ONCE10")
        blocked = rejected(lambda: secure.checkout(b, "alice", "ONCE10"))
        other = secure.checkout(b, "bob", "ONCE10")
        return outcome(first == repeated == 1500, blocked, original == other == 1500,
                       {"vulnerable_repeat_price_cents": repeated, "secure_first_price_cents": original, "secure_repeat_denied": blocked, "redemption_rows": b.execute("SELECT COUNT(*) FROM redemptions").fetchone()[0]})
    finally:
        a.close(); b.close()
