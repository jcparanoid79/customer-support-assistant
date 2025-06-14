# Development Guide

This document provides detailed instructions for developers working on the Customer Support Assistant project.

## Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customer-support-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   make dev-install
   ```

## Development Workflow

### Code Style

We follow PEP 8 with some modifications (defined in `pyproject.toml`):
- Line length: 88 characters (Black default)
- Sorting imports with isort
- Type hints are required

### Running Tests

1. Run all tests:
   ```bash
   make test
   ```

2. Run with coverage:
   ```bash
   make coverage
   ```

3. Run specific test file:
   ```bash
   pytest tests/test_assistant.py -v
   ```

### Documentation

1. Build documentation:
   ```bash
   make docs
   ```

2. Auto-generate API documentation:
   ```bash
   cd docs && sphinx-apidoc -o source/ ../src/
   ```

### Code Quality

1. Format code:
   ```bash
   black src tests
   ```

2. Sort imports:
   ```bash
   isort src tests
   ```

3. Run linter:
   ```bash
   make lint
   ```

## Project Structure

```
RAG_Agent/
├── docs/                    # Documentation
├── src/                    # Source code
│   └── customer_support_assistant/
│       ├── tools/         # Tool implementations
│       └── main.py       # Main assistant logic
├── tests/                 # Test suite
└── requirements.txt      # Project dependencies
```

## Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your changes
3. Add tests
4. Update documentation
5. Run quality checks:
   ```bash
   make lint
   make test
   make docs
   ```

6. Submit a pull request

## Common Tasks

### Adding a New Tool

1. Create a new file in `src/customer_support_assistant/tools/`
2. Implement the tool interface
3. Add to tool registry in `main.py`
4. Add tests in `tests/`
5. Update documentation

### Updating Dependencies

1. Add to `setup.py`
2. Update `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

### Running the Assistant

1. Set environment variables in `.env`
2. Run the assistant:
   ```bash
   python src/run.py
   ```

## Troubleshooting

### Common Issues

1. Import errors:
   - Check PYTHONPATH
   - Verify virtual environment is active
   - Check package installation: `pip list`

2. Test failures:
   - Check test environment
   - Verify dependencies
   - Check mock data

### Getting Help

- Check existing issues
- Review documentation
- Contact maintainers
