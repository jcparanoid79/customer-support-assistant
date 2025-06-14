"""Main module for the Customer Support Assistant."""

import os
import json
import re
from typing import List, TypedDict, Annotated
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import Tool

from .tools.catalog import product_catalog_search
from .tools.orders import order_status_lookup
from .tools.knowledge_base import knowledge_base_query

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is available
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")
os.environ["GOOGLE_API_KEY"] = gemini_api_key

# System prompt configuration
SYSTEM_PROMPT = """You are a helpful customer support assistant. You have access to the following tools:
1. product_catalog_search: Search for product information in our catalog
2. order_status_lookup: Look up the status of customer orders
3. knowledge_base_query: Query our knowledge base for general information about policies and procedures

Always try to use these tools to provide accurate information. If you can't find information using the tools, be honest and say so."""

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash"  # Using the lower-tier flash model
)

# Create the tools
tools = [
    Tool(
        name="product_catalog_search",
        func=product_catalog_search,
        description="Search for product information in the catalog"
    ),
    Tool(
        name="order_status_lookup",
        func=order_status_lookup,
        description="Look up the status of a customer order"
    ),
    Tool(
        name="knowledge_base_query",
        func=knowledge_base_query,
        description="Query the internal knowledge base for general information"
    )
]

class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    agent_outcome: Annotated[List[BaseMessage], {"operator": "add"}]
    intermediate_steps: Annotated[List[BaseMessage], {"operator": "add"}]

def call_llm(state: AgentState):
    messages = state["chat_history"]
    if state["intermediate_steps"]:
        messages.extend(state["intermediate_steps"])
    response = llm.invoke(messages)
    return {"agent_outcome": [response]}

def call_tool(state: AgentState) -> dict:
    """Call the appropriate tool based on the agent's request."""
    last_message = state["agent_outcome"][-1]
    if not hasattr(last_message, "additional_kwargs") or "tool_calls" not in last_message.additional_kwargs:
        return {"intermediate_steps": []}
    
    tool_call = last_message.additional_kwargs["tool_calls"][0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except json.JSONDecodeError:
            pass
    
    # Find the appropriate tool
    for tool in tools:
        if tool.name == tool_name:
            # Extract the first argument if the tool expects a single argument
            if isinstance(tool_args, dict) and len(tool_args) == 1:
                tool_args = next(iter(tool_args.values()))
            response = tool.invoke(tool_args)
            return {"intermediate_steps": [HumanMessage(content=str(response))]}
    
    raise ValueError(f"Tool {tool_name} not found")

def should_continue(state: AgentState) -> str:
    """Determine if we should continue processing or end."""
    last_message = state["agent_outcome"][-1]
    if hasattr(last_message, "additional_kwargs") and "tool_calls" in last_message.additional_kwargs:
        return "tool"
    return "end"

def process_user_input(user_input: str, chat_history: List[BaseMessage] | None = None) -> str:
    """Process a user input and return the response.
    
    Args:
        user_input: The user's input message. Must be a non-empty string.
        chat_history: Optional list of previous chat messages.
        
    Returns:
        str: The assistant's response
        
    Raises:
        ValueError: If user_input is None or empty
    """
    if user_input is None or not user_input.strip():
        raise ValueError("User input cannot be None or empty")

    chat_history = chat_history or []
    user_input_lower = user_input.lower()
    
    # Add system prompt if this is the first message
    if not chat_history:
        chat_history = [HumanMessage(content=SYSTEM_PROMPT)]
    
    # Direct queries that we can handle without LLM
    if "headphone" in user_input_lower:
        return product_catalog_search(user_input)
      # First, try to find matching tools based on keywords
    tool_result = ""
    if any(keyword in user_input_lower for keyword in ["return", "warranty", "shipping", "delivery", "payment", "price", "policy"]):
        tool_result = knowledge_base_query(user_input)    # Check for order status queries
    order_id = extract_order_id(user_input)
    if order_id:
        return order_status_lookup(order_id)
    elif any(product in user_input_lower for product in ["x2000", "camera", "x3000", "display"]):
        tool_result = product_catalog_search(user_input)
    
    # For direct tool results that don't need LLM processing
    if tool_result and any(pattern in user_input_lower for pattern in [
        "list", "show", "what", "tell me about", "details", "specs", "specifications",
        "features", "price", "cost", "how much"
    ]):
        return tool_result
    
    # For more complex queries that need LLM processing
    messages = [HumanMessage(content=SYSTEM_PROMPT)]
    if tool_result:
        messages.append(HumanMessage(content=f"Based on the user's question: '{user_input}', I found this information: {tool_result}\n\nPlease provide a helpful response."))
    else:
        messages.append(HumanMessage(content=f"Please provide a helpful response to: {user_input}"))
    
    response = llm.invoke(messages)
    return str(response.content)

def extract_order_id(text: str) -> str | None:
    """Extract an order ID from text.
    
    Args:
        text: Text that might contain an order ID
        
    Returns:
        The order ID if found, otherwise None
    """
    match = re.search(r'ORD\d+', text.upper())
    return match.group(0) if match else None

def main():
    """Run the customer support assistant in interactive mode."""
    print("Welcome to the Customer Support Assistant!")
    print("Type 'quit' to exit.")
    print("\nHow can I help you today?")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'quit':
                print("\nThank you for using Customer Support Assistant. Goodbye!")
                break
            if user_input:
                response = process_user_input(user_input)
                print(f"\nAssistant: {response}")
        except ValueError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    main()
