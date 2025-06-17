"""Product catalog related tools."""
import re
import difflib
import os
import sys

def product_catalog_search(query: str) -> str:
    """
    Searches the product catalog for information about a specific product.
    Useful for answering questions about product features, specifications, and availability.
    Now robustly matches product names for price queries using fuzzy and substring matching.
    """
    print("DEBUG: product_catalog_search function entered.") # Added for debugging
    # Write the received query to a dedicated log file for debugging
    with open('product_search_queries.log', 'a') as f:
        f.write(f"Received query: '{query}'\n")
    
    # Write to debug log in the main project directory
    sys.stderr.write(f"\n[DEBUG] product_catalog_search called with query: '{query}'\n")
    
    # Normalize query: preserve case, keep hyphens, collapse spaces
    norm_query = re.sub(r'[^a-zA-Z0-9 -]', '', query)  # Preserve hyphens and case
    norm_query = re.sub(r'\s+', ' ', norm_query).strip()

    # Handle empty query
    if not norm_query:
        return "I couldn't find exact matches for your query. Please provide more specific details."

    # Product catalog: name -> price
    products = {
        "sony wh-1000xm5": "$399.99",
        "sony wh-ch720n": "$149.99",
        "sony wh-xb910n": "$249.99",
        "sony wh-1000xm4": "$349.99",
        "bose quietcomfort 45": "$329.99",
        "sennheiser hd 450bt": "$199.99",
        "jbl tune 770nc": "$149.99",
        "apple airpods max": "$549.99",
        "sony headphones": "$199.99",  # Generic entry for Sony headphones
        "sony over-ear headphones": "$299.99"
    }
    norm_products = {re.sub(r'[^a-z0-9 -]', '', k.lower()): v for k, v in products.items()}  # Preserve hyphens
    
    # Write normalized query and products to debug log
    sys.stderr.write(f"[DEBUG] Normalized query: '{norm_query}'\n")
    sys.stderr.write(f"[DEBUG] Products: {norm_products}\n")

    # Always try to match products regardless of specific keywords
    for norm_name, price in norm_products.items():
        sys.stderr.write(f"[DEBUG] Checking product: '{norm_name}' against query: '{norm_query}'\n")
        
        # First check exact match
        if norm_name.lower() == norm_query.lower():
            sys.stderr.write(f"[DEBUG] Exact match found for '{norm_name}'\n")
            return price
            
        # Then check normalized versions without hyphens
        name_no_hyphen = norm_name.replace('-', ' ').lower()
        query_no_hyphen = norm_query.replace('-', ' ').lower()
        if name_no_hyphen == query_no_hyphen:
            sys.stderr.write(f"[DEBUG] Hyphen-agnostic match found for '{norm_name}'\n")
            return price
            
        # Check if product name is substring of query (case-insensitive)
        if norm_name.lower() in norm_query.lower():
            sys.stderr.write(f"[DEBUG] Substring match found for '{norm_name}'\n")
            return price
            
        # Fuzzy match
        if difflib.get_close_matches(norm_name.lower(), [norm_query.lower()], n=1, cutoff=0.8):
            sys.stderr.write(f"[DEBUG] Fuzzy match found for '{norm_name}'\n")
            return price

    sys.stderr.write(f"[DEBUG] No product found for query: '{norm_query}'\n")
    return "Price not found in catalog."
