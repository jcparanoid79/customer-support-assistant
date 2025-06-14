"""Main module for the Customer Support Assistant."""

import os
import json
from typing import List, TypedDict, Annotated
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import Tool
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph

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
            return {"intermediate_steps": [str(response)]}
    
    # If we get here, no matching tool was found
    return {"intermediate_steps": [f"Error: Tool {tool_name} not found"]}
    
    raise ValueError(f"Tool {tool_name} not found")

def should_continue(state: AgentState) -> str:
    """Determine if we should continue processing or end."""
    last_message = state["agent_outcome"][-1]
    if hasattr(last_message, "additional_kwargs") and "tool_calls" in last_message.additional_kwargs:
        return "tool"
    return "end"

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes
workflow.add_node("llm", call_llm)
workflow.add_node("tool", call_tool)

# Set the entry point
workflow.set_entry_point("llm")

# Define the edges
workflow.add_conditional_edges(
    "llm",
    should_continue,
    {
        "tool": "tool",
        "end": END
    }
)
workflow.add_edge("tool", "llm")

# Compile the graph
app = workflow.compile()

def process_user_input(user_input: str, chat_history: List[BaseMessage] | None = None) -> str:
    """Process a user input and return the response using the compiled graph."""
    chat_history = chat_history or []
    
    # Add system prompt if this is the first message
    if not chat_history:
        chat_history = [HumanMessage(content=SYSTEM_PROMPT)]

    # Add the current user input to the chat history
    chat_history.append(HumanMessage(content=user_input))
    
    # Run the graph
    inputs = {"input": user_input, "chat_history": chat_history, "intermediate_steps": []}
    result = app.invoke(inputs)
    
    # Extract the final response from the result
    final_response = result["agent_outcome"][-1].content
    
    # If there are intermediate steps (tool outputs), return the last tool output
    if result.get("intermediate_steps"):
        return result["intermediate_steps"][-1]
    return str(final_response)
