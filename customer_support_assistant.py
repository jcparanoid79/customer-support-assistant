# Set your Google Gemini API key as an environment variable:
# GOOGLE_API_KEY="YOUR_API_KEY"

# Set your LangSmith API key as an environment variable:
# LANGCHAIN_API_KEY="YOUR_API_KEY"
# LANGCHAIN_TRACING_V2="true"
# LANGCHAIN_PROJECT="customer-support-assistant"

import os
import json
from typing import List, TypedDict, Annotated
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import Tool

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is available
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")
os.environ["GOOGLE_API_KEY"] = gemini_api_key

# Google AI configuration is handled via the environment variable; no need to call genai.configure

# Initialize the LLM with the appropriate model
SYSTEM_PROMPT = """You are a helpful customer support assistant. You have access to the following tools:
1. product_catalog_search: Search for product information in our catalog
2. order_status_lookup: Look up the status of customer orders
3. knowledge_base_query: Query our knowledge base for general information about policies and procedures

Always try to use these tools to provide accurate information. If you can't find information using the tools, be honest and say so."""

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash"  # Using the lower-tier flash model
)

def product_catalog_search(query: str) -> str:
    """
    Searches the product catalog for information about a specific product.
    Useful for answering questions about product features, specifications, and availability.
    """
    # This is a placeholder. In a real application, this would query a product database.
    if "X2000 camera" in query:
        return "The X2000 camera is a 24MP mirrorless camera with 4K video capabilities and a 3-inch touchscreen. It comes with a standard 18-55mm lens."
    elif "X3000 display" in query:
        return "The X3000 display is a 27-inch 4K UHD monitor with HDR support and a 144Hz refresh rate. It features multiple input ports including HDMI 2.1 and DisplayPort 1.4."
    return "No information found for the given product."

def order_status_lookup(order_id: str) -> str:
    """
    Looks up the status of a customer order using the order ID.
    Useful for providing updates on shipping, delivery, or order processing.
    """
    # This is a placeholder. In a real application, this would query an order management system.
    if order_id == "ORD12345":
        return "Order ORD12345 is currently in transit and is expected to be delivered by June 20, 2025."
    return "Order not found or invalid order ID."

def knowledge_base_query(query: str) -> str:
    """
    Queries the internal knowledge base for general information, policies, or FAQs.
    Useful for answering questions about return policies, warranty information, or general company procedures.
    """
    # Sample knowledge base responses
    if "return" in query.lower():
        return "Our standard return policy allows returns within 30 days of purchase with original receipt. Items must be in original condition with all packaging and accessories."
    elif "warranty" in query.lower():
        return "All our products come with a standard 1-year manufacturer warranty covering defects in materials and workmanship. Extended warranty options are available at purchase."
    else:
        return "I don't have specific information about that in my knowledge base. Please contact customer support for more details."

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

# We'll handle tool selection manually instead of using bind_tools
# llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    input: str
    chat_history: List[BaseMessage]
    agent_outcome: Annotated[List[BaseMessage], {"operator": "add"}]
    intermediate_steps: Annotated[List[BaseMessage], {"operator": "add"}]

def call_llm(state: AgentState):
    messages = state["chat_history"]
    if state["intermediate_steps"]:
        messages.extend(state["intermediate_steps"])
    response = llm.invoke(messages)  # Use the LLM directly instead of with tools
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
    """Process a user input and return the response."""
    chat_history = chat_history or []
    
    # Add system prompt if this is the first message
    if not chat_history:
        chat_history = [HumanMessage(content=SYSTEM_PROMPT)]
    
    # First, try to find matching tools based on keywords
    tool_result = ""
    if "x2000 camera" in user_input.lower() or "x3000 display" in user_input.lower():
        tool_result = product_catalog_search(user_input)
    elif "ord" in user_input.lower() and "status" in user_input.lower():
        order_id = next((word for word in user_input.split() if word.upper().startswith("ORD")), None)
        if order_id:
            tool_result = order_status_lookup(order_id)
    elif any(keyword in user_input.lower() for keyword in ["return", "warranty", "policy"]):
        tool_result = knowledge_base_query(user_input)
    
    # Now ask the LLM to provide a response using the tool result
    messages = [HumanMessage(content=SYSTEM_PROMPT)]
    if tool_result:
        messages.append(HumanMessage(content=f"Based on the user's question: '{user_input}', I found this information: {tool_result}\n\nPlease provide a helpful response."))
    else:
        messages.append(HumanMessage(content=f"Please provide a helpful response to: {user_input}"))
    
    response = llm.invoke(messages)
    return str(response.content)

# Example usage
if __name__ == "__main__":
    print("Customer Support Assistant initialized!")
    
    # Test cases
    test_questions = [
        "What is your return policy?",
        "Tell me about the X2000 camera.",
        "What is the status of my order ORD12345?",
        "I want to know about your warranty and also what are the features of the X3000 display?"
    ]
    
    for question in test_questions:
        print(f"\n--- Question: {question} ---")
        response = process_user_input(question)
        print(f"Response: {response}")
        print("---")