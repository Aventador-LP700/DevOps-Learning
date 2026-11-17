from .data import ORDERS

def read_order(actor, order_id):
    return dict(ORDERS[order_id])  # Missing object ownership check.
