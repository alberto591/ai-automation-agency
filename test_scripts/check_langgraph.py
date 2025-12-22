import sys
import os
# Add the project root to sys.path
sys.path.append(os.getcwd())

from application.workflows.lead_processing_graph import create_lead_processing_graph

def test_graph():
    print("Testing LangGraph workflow...")
    graph = create_lead_processing_graph()
    
    print("Streaming result from graph...")
    inputs = {"messages": [("user", "What is the capital of Italy?")]}
    
    found_response = False
    for event in graph.stream(inputs):
        for value in event.values():
            content = value["messages"][-1].content
            print(f"Assistant: {content[:50]}...")
            if content:
                found_response = True
    
    if found_response:
        print("LangGraph verification SUCCESSFUL!")
    else:
        print("LangGraph verification FAILED: No response found.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_graph()
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)
