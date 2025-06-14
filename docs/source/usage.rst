Usage
=====

Basic Usage
----------

Running the Assistant
^^^^^^^^^^^^^^^^^^

To start the customer support assistant:

.. code-block:: bash

   python run.py

This will start an interactive session where you can chat with the assistant.

Example Interactions
-----------------

Product Inquiries
^^^^^^^^^^^^^^^

.. code-block:: text

   User: "What headphones do you have under $200?"
   Assistant: "We have several options:
   - HD-100 Basic ($49.99)
   - WL-200 Wireless ($149.99)
   - SP-150 Sport ($179.99)"

Policy Questions
^^^^^^^^^^^^^

.. code-block:: text

   User: "What's your return policy?"
   Assistant: "Our return policy allows returns within 30 days of purchase. 
   Items must be in original condition with packaging..."

Order Status
^^^^^^^^^^

.. code-block:: text

   User: "What's the status of order ORD12345?"
   Assistant: "Order ORD12345 is currently in transit and expected 
   to be delivered by June 20, 2025."

Advanced Usage
------------

Custom Prompts
^^^^^^^^^^^
You can customize the system prompt by modifying the `SYSTEM_PROMPT` variable in `main.py`.

Tool Configuration
^^^^^^^^^^^^^^^
Tools can be configured by modifying their implementations in the `tools/` directory:

* `catalog.py` for product catalog
* `knowledge_base.py` for policies and FAQs
* `orders.py` for order management

Error Handling
^^^^^^^^^^^
The assistant handles various error cases:

* Invalid input
* Missing context
* API failures
* Tool execution errors

Best Practices
------------

1. Be specific with product inquiries
2. Include order numbers when asking about orders
3. One question at a time for best results
4. Follow up if you need clarification
