"""Test cases for each tool in the customer support assistant."""
import pytest
from unittest.mock import patch, MagicMock
from customer_support_assistant.tools.catalog import product_catalog_search
from customer_support_assistant.tools.knowledge_base import knowledge_base_query
from customer_support_assistant.tools.orders import order_status_lookup
from customer_support_assistant.main import process_user_input
from langchain_core.messages import HumanMessage, BaseMessage
from typing import List

class TestProductCatalog:
    """Test cases for the product catalog tool."""
    
    def test_product_search_basic(self):
        """Test basic product search functionality."""
        result = product_catalog_search("Sony over-ear headphones")
        assert "Sony WH-1000XM5" in result
        assert "$399.99" in result
        assert "noise-canceling" in result.lower()

    def test_product_search_categories(self):
        """Test searching by product categories."""
        result = product_catalog_search("headphones")
        assert "over-ear" in result.lower()
        assert "on-ear" in result.lower()
        assert "in-ear" in result.lower()

    def test_product_search_empty(self):
        """Test handling of empty search queries."""
        result = product_catalog_search("")
        assert "provide more specific details" in result.lower()

    def test_product_search_nonexistent(self):
        """Test searching for non-existent products."""
        result = product_catalog_search("nonexistent product xyz")
        assert "couldn't find" in result.lower()

class TestKnowledgeBase:
    """Test cases for the knowledge base tool."""
    
    def test_warranty_query(self):
        """Test warranty information retrieval."""
        result = knowledge_base_query("warranty")
        assert "1-year" in result
        assert "manufacturer warranty" in result.lower()
        assert "extended warranty" in result.lower()

    def test_return_policy(self):
        """Test return policy information retrieval."""
        result = knowledge_base_query("return policy")
        assert "30-day" in result
        assert "original receipt" in result.lower()

    def test_shipping_info(self):
        """Test shipping information retrieval."""
        result = knowledge_base_query("shipping")
        assert "free standard shipping" in result.lower()
        assert "business days" in result.lower()

    def test_payment_info(self):
        """Test payment information retrieval."""
        result = knowledge_base_query("payment methods")
        assert "credit" in result.lower()
        assert "paypal" in result.lower()

class TestOrderStatus:
    """Test cases for the order status tool."""
    
    def test_valid_order(self):
        """Test looking up a valid order."""
        result = order_status_lookup("ORD12345")
        assert "in transit" in result.lower()
        assert "June 20, 2025" in result

    def test_invalid_order(self):
        """Test looking up an invalid order."""
        result = order_status_lookup("INVALID123")
        assert "not found" in result.lower()
        assert "invalid order" in result.lower()

    def test_empty_order_id(self):
        """Test handling of empty order IDs."""
        result = order_status_lookup("")
        assert "not found" in result.lower()

    def test_order_status_lookup_direct(self):
        """Test order_status_lookup directly with a valid ID."""
        result = order_status_lookup("ORD12345")
        assert "in transit" in result.lower()
        assert "June 20, 2025" in result

class TestAssistantIntegration:
    """Integration tests for the complete assistant."""

    @patch('customer_support_assistant.main.ChatGoogleGenerativeAI')
    def test_conversation_flow(self, mock_llm):
        """Test the complete conversation flow."""
        mock_llm.return_value.invoke.return_value = MagicMock(
            content="Here's what I found about the Sony headphones..."
        )

        # Test product inquiry
        response = process_user_input("Tell me about Sony headphones")
        assert "sony" in response.lower()
        assert "headphones" in response.lower()

        # Test policy inquiry
        response = process_user_input("What's your return policy?")
        assert "return" in response.lower()
        assert "30-day" in response.lower()
          # Test direct queries without LLM
        response = process_user_input("Show me headphone specs")
        assert "headphones" in response.lower() and ("categories" in response.lower() or "features" in response.lower())
        # Test order status
        # Test invalid order first
        response = process_user_input("What's the status of order INVALID123?")
        expected_error_message = (
            "Thank you for contacting us.  I'm looking up the status of order INVALID123 using our order_status_lookup tool.\n\n"
            "[Pause while simulating a search]\n\n"
            "Unfortunately, I'm unable to find an order with the ID INVALID123 in our system.  Could you please double-check the order number for any typos or verify it with your order confirmation email?  If you still can't find the correct order number, please provide any other information you have about the order, such as the date it was placed or the items ordered, and I'll do my best to assist you."
        )
        assert response == expected_error_message

        # Test valid order
        response = process_user_input("What's the status of order ORD12345?")
        assert response == "In transit"
        
        # Test price/policy queries
        response = process_user_input("Tell me about shipping costs")
        assert "free standard shipping" in response.lower()
        assert "$50" in response
        
        response = process_user_input("What camera models do you have?")
        assert "x2000" in response.lower() or "x3000" in response.lower()
          # Test with existing chat history
        chat_history: List[BaseMessage] = [HumanMessage(content="Previous message")]
        response = process_user_input("Tell me about warranty", chat_history)
        assert "warranty" in response.lower()
        assert "1-year" in response.lower()

    def test_error_handling(self):
        """Test error handling in the assistant."""
        # Test with empty input
        with pytest.raises(ValueError):
            process_user_input("")
            
        # Test with None chat history (should work fine)
        result = process_user_input("test question", None)
        assert isinstance(result, str)
        assert len(result) > 0
