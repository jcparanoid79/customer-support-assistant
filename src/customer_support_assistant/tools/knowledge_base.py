"""Knowledge base related tools."""

def knowledge_base_query(query: str) -> str:
    """
    Queries the internal knowledge base for general information, policies, or FAQs.
    Useful for answering questions about return policies, warranty information, or general company procedures.
    """
    query = query.lower()
    
    # Returns and Warranty
    if "return" in query:
        return """Return Policy:
- 30-day return period from date of purchase
- Original receipt required
- Item must be in original condition with all packaging and accessories
- Free returns for defective items
- Return shipping fees may apply for non-defective items
- Store credit or refund to original payment method

For online purchases, initiate returns through your account or contact customer support."""
    
    elif "warranty" in query:
        return """Warranty Policy:
- Standard 1-year manufacturer warranty included with all products
- Covers defects in materials and workmanship
- Extended warranty options available at purchase:
  * 2-year extension (+$49.99)
  * 3-year extension (+$79.99)
- Warranty service includes:
  * Free repair or replacement of defective products
  * Technical support
  * Free shipping for warranty service

Contact customer support to initiate a warranty claim."""
    
    # Shipping and Delivery
    elif any(word in query for word in ["shipping", "delivery"]):
        return """Shipping Information:
- Free standard shipping on orders over $50
- Standard shipping: 3-5 business days
- Express shipping: 1-2 business days (additional fee)
- International shipping available to select countries
- Track your order through your account or order confirmation email"""
    
    # Payment and Pricing
    elif any(word in query for word in ["payment", "price", "pricing"]):
        return """Payment Information:
- Accepted payment methods:
  * Credit/Debit cards (Visa, MasterCard, American Express)
  * PayPal
  * Shop Pay
- Secure payment processing
- Price matching available for identical items from major retailers
- Special discounts for students and military (with valid ID)"""
    
    else:
        return """I don't have specific information about that in my knowledge base. For assistance, you can:
1. Contact our customer support team
2. Visit our FAQ page on our website
3. Chat with a live representative during business hours

Our customer support team is available:
Monday-Friday: 9 AM - 8 PM EST
Saturday: 10 AM - 6 PM EST
Sunday: Closed"""
