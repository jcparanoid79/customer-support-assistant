Installation
============

Prerequisites
------------
* Python 3.8 or higher
* pip package manager
* Google Gemini API key

Installation Steps
----------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/yourusername/customer-support-assistant.git
      cd customer-support-assistant

2. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

3. Set up environment variables:

   Create a `.env` file in the project root with:

   .. code-block:: bash

      GEMINI_API_KEY=your_api_key_here

Configuration
------------

Environment Variables
^^^^^^^^^^^^^^^^^^
The following environment variables are required:

* ``GEMINI_API_KEY``: Your Google Gemini API key

Optional environment variables:

* ``LANGCHAIN_TRACING_V2``: Enable LangChain tracing (set to "true")
* ``LANGCHAIN_PROJECT``: Project name for LangChain tracing

Development Installation
---------------------

For development, install additional dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt

This includes:

* pytest for testing
* sphinx for documentation
* flake8 for linting
* black for code formatting
