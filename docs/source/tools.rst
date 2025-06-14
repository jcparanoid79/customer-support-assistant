Tools Documentation
=================

Product Catalog Tool
------------------

The Product Catalog Tool provides access to product information and inventory.

Usage
^^^^^

.. code-block:: python

   from customer_support_assistant.tools.catalog import product_catalog_search

   # Search for products
   result = product_catalog_search("headphones")

Features
^^^^^^^^

* Product search by category
* Price inquiries
* Technical specifications
* Stock availability
* Product comparisons

Knowledge Base Tool
----------------

The Knowledge Base Tool provides access to company policies and procedures.

Usage
^^^^^

.. code-block:: python

   from customer_support_assistant.tools.knowledge_base import knowledge_base_query

   # Query policies
   result = knowledge_base_query("return policy")

Features
^^^^^^^^

* Policy information
* FAQs
* Shipping information
* Payment details
* Warranty terms

Order Status Tool
--------------

The Order Status Tool manages order-related inquiries.

Usage
^^^^^

.. code-block:: python

   from customer_support_assistant.tools.orders import order_status_lookup

   # Look up order status
   result = order_status_lookup("ORD12345")

Features
^^^^^^^^

* Order tracking
* Delivery estimates
* Order history
* Shipping updates

Tool Development
-------------

Creating New Tools
^^^^^^^^^^^^^^^

1. Create a new module in `tools/`
2. Implement the required interface
3. Register the tool in `main.py`

Example:

.. code-block:: python

   from langchain_core.tools import Tool

   def my_tool_function(query: str) -> str:
       # Implementation
       return result

   new_tool = Tool(
       name="my_tool",
       func=my_tool_function,
       description="Tool description"
   )
