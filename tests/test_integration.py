"""Integration tests for the customer support assistant."""
from unittest.mock import patch, MagicMock
from customer_support_assistant.main import process_user_input
from langchain_core.messages import HumanMessage, BaseMessage
from typing import List
from customer_support_assistant.tools.orders import order_status_lookup

class TestAssistantOrderHandling:
    """Test order status handling functionality."""

    def test_order_lookup_with_valid_order(self):
        """Test looking up a valid order."""
        response = process_user_input("Check order ORD12345")
        assert response == "In transit"
        assert "june 20" in response.lower()

    def test_order_lookup_with_invalid_order(self):
        """Test looking up an invalid order."""
        response = process_user_input("Check order INVALID123")
        assert "not found" in response.lower() or "invalid" in response.lower()

    def test_order_lookup_different_formats(self):
        """Test order lookup with different input formats."""
        # Direct order ID
        response = process_user_input("ORD12345 status")
        assert response == "In transit"

        # Natural language query
        response = process_user_input("What's happening with ORD12345")
        assert response == "In transit"

        # With other text
        response = process_user_input("I ordered something with id ORD12345 last week")
        assert response == "In transit"

    def test_order_status_lookup_direct_integration(self):
        """Test order_status_lookup directly with a valid ID in integration test."""
        result = order_status_lookup("ORD12345")
        assert "in transit" in result.lower()
        assert "June 20, 2025" in result


    @patch('customer_support_assistant.main.ChatGoogleGenerativeAI')
    def test_order_lookup_with_llm(self, mock_llm):
        """Test order lookup with LLM integration."""
        mock_llm.return_value.invoke.return_value = MagicMock(
            content="Let me check that order for you..."
        )

        # Test with chat history
        chat_history: List[BaseMessage] = [HumanMessage(content="Previous message")]
        response = process_user_input("Track ORD12345", chat_history)
        assert "in transit" in response.lower()
        assert "june 20" in response.lower()

        # Test with complex query
        response = process_user_input("I haven't received ORD12345 yet, where is it?")
        assert "in transit" in response.lower()
        assert "june 20" in response.lower()
