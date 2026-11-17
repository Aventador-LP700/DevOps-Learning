def checkout(db, user, coupon, subtotal_cents=2500):
    if coupon != "ONCE10":
        raise ValueError("Unknown coupon")
    return subtotal_cents - 1000  # No redemption state; each request gets a discount.
