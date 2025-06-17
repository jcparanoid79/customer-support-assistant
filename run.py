#!/usr/bin/env python
"""CLI interface for the Customer Support Assistant."""

from customer_support_assistant.main import process_user_input

import sys
import time # Import time module

def main():
    """Run the customer support assistant in interactive mode."""
    print("Customer Support Assistant initialized!")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    try:
        for line in sys.stdin:
            user_input = line.strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using our Customer Support Assistant. Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                response = process_user_input(user_input)
                print(f"\nAssistant: {response}")
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again or contact system administrator if the issue persists.")
            
            # Flush output to ensure all messages are displayed
            sys.stdout.flush()
            sys.stderr.flush() # Explicitly flush stderr
            time.sleep(0.1) # Add a small delay
    except EOFError:
        pass # Handle EOF when input is piped
    finally:
        pass # No stderr to restore

if __name__ == "__main__":
    main()
