import sqlite3
from labs.support import Denied

def checkout(db, user, coupon, subtotal_cents=2500):
    if not isinstance(user, str) or not user.strip() or len(user) > 128:
        raise Denied("Authenticated principal required")
    if coupon != "ONCE10" or not isinstance(subtotal_cents, int) or subtotal_cents < 1000:
        raise Denied("Invalid coupon or subtotal")
    try:
        # UNIQUE(user, coupon) enforces one redemption atomically in the database.
        with db:
            db.execute("INSERT INTO redemptions (user, coupon) VALUES (?, ?)", (user, coupon))
    except sqlite3.IntegrityError as exc:
        raise Denied("Coupon already redeemed") from exc
    return subtotal_cents - 1000
