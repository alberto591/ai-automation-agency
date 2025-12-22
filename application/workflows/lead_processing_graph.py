import os
from typing import Annotated, TypedDict

from langchain_mistralai import ChatMistralAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from config.settings import settings

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def create_lead_processing_graph():
    # Initialize the LLM
    llm = ChatMistralAI(
        mistral_api_key=settings.MISTRAL_API_KEY,
        model=settings.MISTRAL_MODEL,
    )

    # Define the function that calls the model
    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    # Define a new graph
    workflow = StateGraph(State)

    # Define the two nodes we will cycle between
    workflow.add_node("chatbot", chatbot)

    # Set the entrypoint as `chatbot`
    workflow.add_edge(START, "chatbot")

    # We want our chatbot to end after one response
    workflow.add_edge("chatbot", END)

    # Compile the graph
    return workflow.compile()

# Example usage (uncomment to test manually if needed)
# if __name__ == "__main__":
#     graph = create_lead_processing_graph()
#     for event in graph.stream({"messages": [("user", "Hello, I am interested in a property in Milan.")]}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)
