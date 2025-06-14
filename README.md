# Customer Support Assistant

A RAG-based customer support assistant using LangChain, Google Gemini, and Chroma vector store.

## Features

- Product catalog search
- Order status lookup
- Knowledge base querying
- Natural language understanding
- Context-aware responses

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .\.venv\Scripts\activate   # Windows
   ```

3. Install for development:
   ```bash
   pip install -e ".[dev,docs]"
   ```

4. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```

5. Update the `.env` file with your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Development

1. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

2. Run tests:
   ```bash
   pytest -v --cov=src
   ```

3. Build documentation:
   ```bash
   cd docs
   make html
   ```

4. Format code:
   ```bash
   black src tests
   isort src tests
   ```

## Usage

Run the customer support assistant:

```bash
python -m customer_support_assistant.main
```

Example questions you can ask:
- "What is your return policy?"
- "Tell me about the X2000 camera."
- "What is the status of my order ORD12345?"
- "What are the features of the X3000 display?"

## Project Structure

```
.
├── customer_support_assistant/   # Main package directory
│   ├── __init__.py             # Package initialization
│   ├── main.py                 # Main script
│   └── tools/                  # Tool implementations
│       └── __init__.py
├── requirements.txt            # Project dependencies
├── .env.example               # Example environment variables
└── README.md                  # Project documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
