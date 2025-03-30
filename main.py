import os
import streamlit as st

# Optionally set API keys from environment variables or use Streamlit secrets.
# If you use Streamlit Cloud, you can add your keys to the secrets.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")

# Import LangGraph and related dependencies.
from typing import Annotated
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Define the conversation state schema.
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Instantiate the search tool (Tavily) with a limit of 2 results per query.
tool = TavilySearchResults(max_results=2)
tools = [tool]

# Create an instance of the Anthropic LLM.
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
# Bind the tools to the LLM so that it can output structured tool calls when needed.
llm_with_tools = llm.bind_tools(tools)

# Define the chatbot node: it takes the current state and produces a new message.
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

# Build the state graph.
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Set up conditional routing: if the chatbot's output includes tool calls, route to the tools node.
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile the graph with a MemorySaver checkpointer to enable conversation memory.
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# --- Streamlit UI Setup ---
st.title("Thechtabot Chatbot")
st.markdown("Welcome to Thechtabot! Start chatting below. Type 'quit', 'exit', or 'q' to reset.")

# Initialize conversation state in session_state if it doesn't exist.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to run a conversation turn using the LangGraph graph.
def run_turn(user_message: str):
    # Append the user's new message to the conversation history.
    st.session_state.messages.append({"role": "user", "content": user_message})
    # Prepare the state dictionary.
    state = {"messages": st.session_state.messages}
    # Run the graph stream and capture the final assistant message.
    assistant_response = ""
    try:
        for event in graph.stream(state, {}, stream_mode="values"):
            if "messages" in event:
                # Get the last message from the assistant.
                assistant_message = event["messages"][-1]
                assistant_response = assistant_message.content
        # Append the assistant's response to the conversation history.
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    except Exception as e:
        assistant_response = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    return assistant_response

# Display the conversation history.
st.header("Conversation")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**User:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")

# User input form.
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:")
    submit_button = st.form_submit_button("Send")

if submit_button:
    if user_input.lower() in ["quit", "exit", "q"]:
        st.session_state.messages = []
        st.experimental_rerun()
    else:
        with st.spinner("Assistant is typing..."):
            response = run_turn(user_input)
        st.experimental_rerun()
