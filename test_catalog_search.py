import os
import sys
from src.customer_support_assistant.tools.catalog import product_catalog_search

# No redirection of stderr for this test, print directly to console
try:
    query = "How much is the Sony WH-1000XM5?"
    result = product_catalog_search(query)
    print(f"Result for '{query}': {result}")
finally:
    pass # No stderr to restore
