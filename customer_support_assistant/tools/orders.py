"""Order management related tools."""

def order_status_lookup(order_id: str) -> str:
    """Look up the status of a customer order by order ID."""
    # Mock database of orders
    orders = {
        "ORD12345": "In transit",
        "ORD67890": "Delivered",
        "ORD11121": "Processing"
    }
    return orders.get(order_id, "Order not found or invalid order ID.")
