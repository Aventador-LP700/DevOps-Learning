from labs.support import Denied
from .data import ORDERS

def read_order(actor, order_id):
    order = ORDERS.get(order_id)
    if order is None or order["owner"] != actor:
        raise Denied("Order unavailable")
    return dict(order)
