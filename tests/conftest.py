"""Test configuration and fixtures for the customer support assistant."""
import pytest
from pathlib import Path
import sys

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.append(src_path)

@pytest.fixture
def mock_gemini_api_key():
    """Provide a mock API key for testing."""
    return "test_api_key_12345"

@pytest.fixture
def mock_catalog_data():
    """Provide mock product catalog data for testing."""
    return {
        "headphones": {
            "Sony WH-1000XM5": {
                "price": 399.99,
                "type": "over-ear",
                "features": ["noise-canceling", "wireless"]
            }
        }
    }

@pytest.fixture
def mock_knowledge_base():
    """Provide mock knowledge base data for testing."""
    return {
        "return_policy": "30-day return period",
        "warranty": "1-year standard warranty"
    }

@pytest.fixture
def mock_order_data():
    """Provide mock order data for testing."""
    return {
        "ORD12345": {
            "status": "in transit",
            "delivery_date": "2025-06-20"
        }
    }
