"""Main module for the Customer Support Assistant."""

import os
import json
import re
import sys
from typing import List, TypedDict, Annotated
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from customer_support_assistant.tools.catalog import product_catalog_search
from customer_support_assistant.tools.orders import order_status_lookup
from customer_support_assistant.tools.knowledge_base import knowledge_base_query

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is available
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")
os.environ["GOOGLE_API_KEY"] = gemini_api_key

# System prompt configuration
SYSTEM_PROMPT = """You are a helpful customer support assistant. You have access to the following tools:
1. product_catalog_search: Search for product information in our catalog (use 'query' parameter)
2. order_status_lookup: Look up the status of customer orders (use 'order_id' parameter)
3. knowledge_base_query: Query our knowledge base for general information (use 'query' parameter)

CRITICAL RULES - FOLLOW EXACTLY:
1. When using a tool, output ONLY pure JSON with tool calls. Example:
{
  "tool_calls": [
    {
      "name": "product_catalog_search",
      "args": {
        "query": "Sony WH-1000XM5"
      }
    }
  ]
}

2. NEVER add any text before or after the JSON
3. NEVER explain that you're using a tool
4. NEVER show the tool call as code or in any formatted way
5. NEVER wrap the JSON in markdown code blocks
6. NEVER include conversational text like "please hold" or "I'll search"
7. If a tool provides a direct answer, return ONLY the tool's response
8. If no tool is needed, respond with your answer ONLY (no explanations)
9. Your response must be either:
   - Pure JSON with tool calls
   - A direct answer without any formatting

VIOLATING THESE RULES WILL CAUSE SYSTEM FAILURES. STRICTLY FOLLOW THEM.

FAILURE EXAMPLES:
BAD: Please hold while I search our product catalog...
BAD: ```json
{
  "tool_calls": [
    {
      "name": "product_catalog_search",
      "args": {"query": "Sony WH-1000XM5"}
    }
  ]
}
```
GOOD: {
  "tool_calls": [
    {
      "name": "product_catalog_search",
      "args": {"query": "Sony WH-1000XM5"}
    }
  ]
}"""

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash"  # Using the lower-tier flash model
)

# Create the tools
tools = [
    Tool(
        name="product_catalog_search",
        func=product_catalog_search,
        description="Search for product information in the catalog. Use the 'query' parameter to specify the product name or details (e.g., query='Sony WH-1000XM5')."
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
    # Create a new messages list starting with the system prompt
    messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    
    # Append the chat history
    messages.extend(state["chat_history"])
    
    # Append the user input as a HumanMessage
    messages.append(HumanMessage(content=state["input"]))
    
    # Append intermediate steps as separate messages
    intermediate_steps = state.get("intermediate_steps", [])
    if intermediate_steps:
        messages.extend(intermediate_steps)
    
    response = llm.invoke(messages)
    
    # Log the full LLM response to a file
    log_path = os.path.join(os.getcwd(), 'llm_responses.log')
    with open(log_path, 'a') as f:
        f.write(f"LLM Response: {response}\n")
        f.write(f"Response Content: {response.content}\n")
        f.write(f"Additional Kwargs: {getattr(response, 'additional_kwargs', 'N/A')}\n")
        f.write("-----\n")
    
    # Also write to a separate debug log
    debug_log_path = os.path.join(os.getcwd(), 'debug.log')
    with open(debug_log_path, 'a') as f:
        f.write(f"[LLM DEBUG] Response: {response}\n")
        f.write(f"[LLM DEBUG] Content: {response.content}\n")
        f.write(f"[LLM DEBUG] Kwargs: {getattr(response, 'additional_kwargs', 'N/A')}\n")
        f.write(f"[LLM DEBUG] Log written to: {log_path}\n")
    
    # Print to stderr
    sys.stderr.write(f"[LLM DEBUG] Response logged to {log_path}\n")
    sys.stderr.write(f"[LLM DEBUG] Debug details written to {debug_log_path}\n")
    
    from langchain_core.messages import AIMessage
    
    # Create a clean response object
    clean_response = AIMessage(content="", additional_kwargs={})
    
    # Extract tool calls from additional_kwargs if available
    if hasattr(response, "additional_kwargs") and "tool_calls" in response.additional_kwargs:
        clean_response.additional_kwargs = {"tool_calls": response.additional_kwargs["tool_calls"]}
        return {"agent_outcome": [clean_response]}
    
    # Handle different content types safely
    if isinstance(response.content, str):
        content_str = response.content
    elif isinstance(response.content, list):
        # Convert list elements to strings
        content_str = " ".join(str(item) for item in response.content)
    else:
        content_str = str(response.content)
    
    # If we don't have tool calls from additional_kwargs, check the content string
    if not clean_response.additional_kwargs.get("tool_calls"):
        # Check if the content string is a JSON string that contains tool_calls
        if isinstance(content_str, str):
            try:
                # Try to parse as JSON - first check for raw JSON
                parsed = json.loads(content_str)
                if "tool_calls" in parsed and isinstance(parsed["tool_calls"], list):
                    clean_response.additional_kwargs = {"tool_calls": parsed["tool_calls"]}
                    return {"agent_outcome": [clean_response]}
            except json.JSONDecodeError:
                # If that fails, check for JSON in markdown code blocks
                try:
                    # Extract JSON from markdown code block
                    json_match = re.search(r'```json\n({.*?})\n```', content_str, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(1))
                        if "tool_calls" in parsed and isinstance(parsed["tool_calls"], list):
                            clean_response.additional_kwargs = {"tool_calls": parsed["tool_calls"]}
                            return {"agent_outcome": [clean_response]}
                except:
                    # Not JSON, so we'll treat as a direct answer
                    pass

    # If we have tool calls at this point, return them
    if clean_response.additional_kwargs.get("tool_calls"):
        return {"agent_outcome": [clean_response]}

    # Otherwise, return the content as a direct answer
    return {"agent_outcome": [AIMessage(content=content_str)]}

def call_tool(state: AgentState) -> dict:
    """Call the appropriate tool based on the agent's request."""
    print("DEBUG: call_tool function entered.") # Debug print
    last_message = state["agent_outcome"][-1]
    print(f"DEBUG: last_message: {last_message}") # Debug print
    
    # Extract tool call information - handle different message types
    tool_call = None
    
    # Check for tool calls in additional_kwargs
    if hasattr(last_message, "additional_kwargs") and last_message.additional_kwargs and "tool_calls" in last_message.additional_kwargs:
        tool_call = last_message.additional_kwargs["tool_calls"][0]
    
    # If not found, try to parse tool calls from content if it's a string
    elif isinstance(getattr(last_message, "content", None), str):
        content_str = str(last_message.content)
        
        # Try to extract JSON from content string
        try:
            # Look for JSON in the content
            json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
            if json_match:
                content = json.loads(json_match.group())
                if "tool_calls" in content:
                    tool_call = content["tool_calls"][0]
        except json.JSONDecodeError:
            pass  # Content is not JSON, skip
    
    if not tool_call:
        print("DEBUG: No tool_calls found.") # Debug print
        return {"intermediate_steps": []}
    
    # Extract tool name and arguments with proper type checking
    tool_name = tool_call.get("name") if isinstance(tool_call, dict) else None
    tool_args = tool_call.get("args") if isinstance(tool_call, dict) else None
    
    if not tool_name or not tool_args:
        print("DEBUG: Tool call missing name or args.") # Debug print
        return {"intermediate_steps": []}
    
    print(f"DEBUG: Tool to call: {tool_name} with args: {tool_args}") # Debug print

    # Log tool call to a temporary file
    with open('tool_calls.log', 'a') as f:
        f.write(f"Tool Called: {tool_name}\n")
        f.write(f"Arguments: {tool_args}\n")
    
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
            print(f"DEBUG: tool_args after JSON load: {tool_args}") # Debug print
        except json.JSONDecodeError:
            print(f"DEBUG: tool_args is string but not JSON: {tool_args}") # Debug print
            pass
    
    # Find the appropriate tool
    for tool in tools:
        if tool.name == tool_name:
            # Special handling for product_catalog_search to ensure 'query' argument
            if tool_name == "product_catalog_search":
                if isinstance(tool_args, dict) and "product_name" in tool_args:
                    tool_args["query"] = tool_args.pop("product_name")
                    sys.stderr.write(f"[DEBUG] Remapped product_name to query for product_catalog_search. New args: {tool_args}\n")
                    print(f"DEBUG: Remapped product_name to query. New args: {tool_args}") # Debug print
                elif isinstance(tool_args, str) and not tool_args.startswith('{'): # If it's a string, assume it's the query
                    tool_args = {"query": tool_args}
                    sys.stderr.write(f"[DEBUG] Wrapped string arg in query for product_catalog_search. New args: {tool_args}\n")
                    print(f"DEBUG: Wrapped string arg in query. New args: {tool_args}") # Debug print
                    
            # Special handling for knowledge_base_query to ensure 'query' argument
            if tool_name == "knowledge_base_query":
                if isinstance(tool_args, dict) and "question" in tool_args:
                    tool_args["query"] = tool_args.pop("question")
                    sys.stderr.write(f"[DEBUG] Remapped question to query for knowledge_base_query. New args: {tool_args}\n")
                    print(f"DEBUG: Remapped question to query. New args: {tool_args}") # Debug print
                elif isinstance(tool_args, str) and not tool_args.startswith('{'): # If it's a string, assume it's the query
                    tool_args = {"query": tool_args}
                    sys.stderr.write(f"[DEBUG] Wrapped string arg in query for knowledge_base_query. New args: {tool_args}\n")
                    print(f"DEBUG: Wrapped string arg in query. New args: {tool_args}") # Debug print

            # Special handling for product_catalog_search to ensure 'query' argument
            if tool_name == "product_catalog_search":
                if isinstance(tool_args, dict) and "product_name" in tool_args:
                    tool_args["query"] = tool_args.pop("product_name")
                    sys.stderr.write(f"[DEBUG] Remapped product_name to query for product_catalog_search. New args: {tool_args}\n")
                    print(f"DEBUG: Remapped product_name to query. New args: {tool_args}") # Debug print
                elif isinstance(tool_args, str) and not tool_args.startswith('{'): # If it's a string, assume it's the query
                    tool_args = {"query": tool_args}
                    sys.stderr.write(f"[DEBUG] Wrapped string arg in query for product_catalog_search. New args: {tool_args}\n")
                    print(f"DEBUG: Wrapped string arg in query. New args: {tool_args}") # Debug print
            
            print(f"DEBUG: Invoking tool {tool.name} with final args: {tool_args}") # Debug print
            try:
                response = tool.invoke(tool_args)
            except Exception as e:
                response = f"Error calling tool {tool.name}: {str(e)}"
                print(f"ERROR: {response}") # Debug print
            print(f"DEBUG: Tool response: {response}") # Debug print

            # For product_catalog_search, return just the price if found
            if tool_name == "product_catalog_search" and isinstance(response, str) and response.startswith('$'):
                return {"intermediate_steps": [HumanMessage(content=response)]}
            
            return {"intermediate_steps": [HumanMessage(content=str(response))]}
    
    print(f"DEBUG: Tool {tool_name} not found.") # Debug print
    raise ValueError(f"Tool {tool_name} not found")

def should_continue(state: AgentState) -> str:
    """Determine if we should continue processing or end."""
    last_message = state["agent_outcome"][-1]
    # If the LLM returned a tool call, then we call the tool
    if hasattr(last_message, "additional_kwargs") and "tool_calls" in last_message.additional_kwargs:
        print("DEBUG: should_continue returning 'tool' (tool_calls detected).") # Debug print
        return "tool"
    # Otherwise, we end the conversation
    print("DEBUG: should_continue returning 'end' (no tool_calls detected).") # Debug print
    return "end"

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("llm", call_llm)
workflow.add_node("tool", call_tool)

workflow.set_entry_point("llm")

workflow.add_conditional_edges(
    "llm",
    should_continue,
    {
        "tool": "tool",
        "end": END
    }
)
workflow.add_edge("tool", "llm")

# Set step limit to prevent infinite loops
app = workflow.compile(
    checkpointer=MemorySaver()
)

# Create a debug log file
with open('langgraph_debug.log', 'w') as f:
    f.write("LangGraph Debug Log\n")
    f.write("===================\n\n")

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
    sys.stderr.write(f"\n[DEBUG] process_user_input called with user_input: '{user_input}'\n")
    if user_input is None or not user_input.strip():
        raise ValueError("User input cannot be None or empty")

    # Clear previous debug log
    debug_log_path = os.path.join(os.getcwd(), 'langgraph_debug.log')
    with open(debug_log_path, 'w') as f:
        f.write(f"Starting new session with input: {user_input}\n\n")
    sys.stderr.write(f"[DEBUG] Debug log cleared: {debug_log_path}\n")

    chat_history = chat_history or []
    user_input_lower = user_input.lower()

    # Use the LangChain graph to process the input
    inputs = {"input": user_input, "chat_history": chat_history}
    
    # Iterate through the stream of states from the LangChain graph
    final_response = "I'm sorry, I couldn't process your request."
    # Provide a dummy thread_id for MemorySaver
    config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    for s in app.stream(inputs, config=config):
        # Log each state to debug file
        with open('langgraph_debug.log', 'a') as f:
            f.write(f"State: {s}\n\n")
        
        if "__end__" in s:
            # When the end state is reached, process the final state
            final_state = s["__end__"]
            sys.stderr.write(f"[DEBUG] Final state: {final_state}\n")
            
            # Log final state to debug file
            with open('langgraph_debug.log', 'a') as f:
                f.write(f"Final State: {final_state}\n")
            
            # Return the latest tool output if available
            if final_state.get("intermediate_steps"):
                latest_tool_output = str(final_state["intermediate_steps"][-1].content)
                sys.stderr.write(f"[DEBUG] Returning latest tool output: '{latest_tool_output}'\n")
                return latest_tool_output
            
            # If no tool output, return the agent's final response
            if final_state.get("agent_outcome"):
                final_response = str(final_state["agent_outcome"][-1].content)
                sys.stderr.write(f"[DEBUG] Agent outcome used as final response: '{final_response}'\n")
                return final_response
            
            sys.stderr.write(f"[DEBUG] No outcome or intermediate steps.\n")
            return "I'm sorry, I couldn't process your request."
        else:
            # If it's not the end state, log the stream for debugging
            sys.stderr.write(f"[DEBUG] Stream: {s}\n")
            
            # Check if we have a direct answer from the LLM
            if 'llm' in s and s['llm'].get("agent_outcome"):
                agent_outcome = s['llm']["agent_outcome"][-1]
                if not agent_outcome.additional_kwargs.get("tool_calls") and agent_outcome.content:
                    final_response = agent_outcome.content
                    sys.stderr.write(f"[DEBUG] Storing direct response: '{final_response}'\n")
    
    sys.stderr.write(f"[DEBUG] Stream ended without final state. Returning last stored response.\n")
    return final_response


def extract_order_id(user_input: str) -> str | None:
    """Extract an order ID from text.
    
    Args:
        text: Text that might contain an order ID
        
    Returns:
        The order ID if found, otherwise None
    """
    match = re.search(r'ORD\d+', user_input.upper())
    return match.group(0) if match else None

def main():
    """Run the customer support assistant in interactive mode."""
    print("Welcome to the Customer Support Assistant!")
    print("Type 'quit' to exit.")
    print("\nHow can I help you today?")

    # Create test scenario that will trigger rule violation
    test_input = "What's the price of Sony headphones?"
    print(f"\nRunning test scenario: {test_input}")
    test_response = process_user_input(test_input)
    print(f"\nTest Assistant: {test_response}")
    
    # Run interactive mode
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'quit':
                print("\nThank you for using our Customer Support Assistant. Goodbye!")
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
