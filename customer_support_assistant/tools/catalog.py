"""Product catalog related tools."""

import json

def product_catalog_search(query: str) -> str:
    """
    Searches the product catalog for information about a specific product.
    Useful for answering questions about product features, specifications, and availability.
    """
    query = query.lower()
    
    # Specific product search
    if "wh-1000xm5" in query:
        return json.dumps({
            "name": "Sony WH-1000XM5",
            "description": "Premium noise-canceling headphones with up to 30 hours battery life, multipoint connection, and advanced noise canceling",
            "price": 399.99
        }, ensure_ascii=False)
    
    # Headphones catalog
    if "sony" in query and "over-ear" in query:
        return """Available Sony over-ear headphones:
1. Sony WH-1000XM5: Premium noise-canceling headphones with up to 30 hours battery life, multipoint connection, and advanced noise canceling. Price: $399.99
2. Sony WH-CH720N: Lightweight wireless noise-canceling headphones with up to 35 hours battery life. Price: $149.99
3. Sony WH-XB910N: EXTRA BASS wireless noise-canceling headphones with up to 30 hours battery life. Price: $249.99"""
    
    elif "over-ear" in query and "headphone" in query:
        return """Available over-ear headphones:
1. Sony WH-1000XM5: Premium noise-canceling headphones. Price: $399.99
2. Bose QuietComfort 45: Wireless noise-canceling headphones. Price: $329.99
3. Sennheiser HD 450BT: Wireless noise-canceling headphones. Price: $199.99
4. Sony WH-CH720N: Budget-friendly wireless noise-canceling. Price: $149.99"""
    
    elif "headphone" in query:
        return """Our headphone categories:
1. Over-ear headphones: Best for sound quality and noise isolation
2. On-ear headphones: Compact but comfortable
3. In-ear headphones: Portable and lightweight
4. True wireless earbuds: Complete freedom from wires

Popular brands: Sony, Bose, Sennheiser, Apple, Samsung
Price range: $29.99 - $399.99

For specific recommendations, please specify:
- Type (over-ear, on-ear, in-ear, true wireless)
- Brand preference (if any)
- Price range
- Must-have features (noise-canceling, water resistance, etc.)"""

    # Cameras catalog
    elif "x2000 camera" in query:
        return "The X2000 camera is a 24MP mirrorless camera with 4K video capabilities and a 3-inch touchscreen. It comes with a standard 18-55mm lens. Price: $899.99"
    
    # Displays catalog
    elif "x3000 display" in query:
        return "The X3000 display is a 27-inch 4K UHD monitor with HDR support and a 144Hz refresh rate. It features multiple input ports including HDMI 2.1 and DisplayPort 1.4. Price: $499.99"
    
    return "I couldn't find exact matches for your query. To help you better, please provide more specific details about what you're looking for, such as:\n- Product category\n- Brand preference\n- Price range\n- Specific features"
