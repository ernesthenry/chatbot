from typing import Annotated
from typing_extensions import TypedDict
import os
import getpass

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("ANTHROPIC_API_KEY")
_set_env("TAVILY_API_KEY")

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults

# Import LangGraph components for state, graph building, and memory checkpointing
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Define the state schema: our conversation consists of a list of messages.
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Instantiate the search tool (Tavily) with a limit of 2 results per query.
tool = TavilySearchResults(max_results=2)
tools = [tool]

# Create an instance of the Anthropic LLM (using Claude 3.5 in this example)
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
# Bind the tools to the LLM so that it can output structured tool calls when needed.
llm_with_tools = llm.bind_tools(tools)

# Define the chatbot node: it takes the current state and produces a new message.
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

# Build the graph that orchestrates the conversation.
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Configure conditional routing: if the chatbot's response includes tool calls, route to the "tools" node.
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Enable conversation memory by compiling the graph with a MemorySaver checkpointer.
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Run the chatbot in an interactive loop.
if __name__ == "__main__":
    print("Chatbot is running. Type 'quit', 'exit', or 'q' to stop.")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            for event in graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                {},
                stream_mode="values",
            ):
                if "messages" in event:
                    assistant_message = event["messages"][-1]
                    print("Assistant:", assistant_message.content)
        except Exception as e:
            print("Error during processing:", e)
            break
