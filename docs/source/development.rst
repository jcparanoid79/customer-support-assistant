Development Guide
================

Setting Up Development Environment
-------------------------------

1. Clone the repository
2. Install development dependencies
3. Set up pre-commit hooks
4. Configure your IDE

Code Style
---------

We follow PEP 8 with these additions:

* Line length: 88 characters (Black default)
* Docstring style: Google
* Type hints: Required

Example:

.. code-block:: python

   def process_query(query: str) -> dict:
       """Process a user query and return results.
       
       Args:
           query: The user's input query
           
       Returns:
           A dictionary containing the processed results
           
       Raises:
           ValueError: If the query is empty
       """
       if not query:
           raise ValueError("Query cannot be empty")
       # Implementation

Testing
-------

Running Tests
^^^^^^^^^^^

.. code-block:: bash

   python -m pytest

Writing Tests
^^^^^^^^^^^

.. code-block:: python

   def test_product_search():
       """Test product search functionality."""
       result = product_catalog_search("headphones")
       assert "headphones" in result.lower()

Test Coverage
^^^^^^^^^^^

.. code-block:: bash

   python -m pytest --cov=customer_support_assistant

Documentation
-----------

Building Docs
^^^^^^^^^^^

.. code-block:: bash

   cd docs
   make html

Writing Docs
^^^^^^^^^^

* Use RST format
* Include docstrings
* Add usage examples
* Document exceptions

Releasing
--------

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run tests
5. Build documentation
6. Create pull request
