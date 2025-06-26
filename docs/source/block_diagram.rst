RAG Agent Block Diagram
===================

.. code-block::

    +-------------------+     +-----------------+     +------------------+
    |   User Interface  |     |  LLM Pipeline   |     |   Tool Router    |
    |                   +---->|   (Gemini 1.5)  +---->|                  |
    |  - Input handling |     |  - Processing   |     | - Tool selection |
    |  - Response format|     |  - Generation   |     | - Route requests |
    +-------------------+     +-----------------+     +--------+---------+
            ^                                                  |
            |                                                  v
            |                 +------------------+    +------------------+
            |                 |  Product Catalog |    | Knowledge Base  |
            |                 |                  |<---+                  |
            |                 |  - Search        |    | - Policies      |
            |                 |  - Prices        |    | - FAQs          |
            |                 |  - Features      |    | - Procedures    |
            |                 +--------+---------+    +------------------+
            |                          |
            |                          v
    +-------+---------+     +------------------+     +------------------+
    |   Response      |     |   Order System   |     |    Logging &    |
    |   Generator     |<----+                  |     |   Monitoring    |
    |                 |     |  - Status        |     |                 |
    |  - Formatting   |     |  - Tracking      |     | - Debug logs   |
    |  - Integration  |     |  - Updates       |     | - Error tracks  |
    +-----------------+     +------------------+     +------------------+

Flow Description:
1. User input is received and processed
2. LLM pipeline understands intent and context
3. Tool router selects appropriate tool(s)
4. Tools process request and retrieve information
5. Response generator formats final output
6. Logging system tracks all operations
