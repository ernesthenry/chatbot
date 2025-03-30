import os
import streamlit as st
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from dotenv import load_dotenv
import uuid

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    st.error("Missing OpenAI API Key! Set OPENAI_API_KEY in environment variables or Streamlit secrets.")
    st.stop()

if not TAVILY_API_KEY:
    st.error("Missing Tavily API Key! Set TAVILY_API_KEY in environment variables or Streamlit secrets.")
    st.stop()

# Define the conversation state schema.
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Instantiate the search tool (Tavily)
tool = TavilySearchResults(max_results=2)
tools = [tool]

# Create an instance of OpenAI LLM with a model you have access to
# Changed from "gpt-4" to "gpt-3.5-turbo" which is more commonly available
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
llm_with_tools = llm.bind_tools(tools)

# Define the chatbot node
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

# Build the state graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile the graph with a MemorySaver checkpointer
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# --- Streamlit UI Setup ---
st.title("Chatbot powered by OpenAI & LangGraph")
st.markdown("Start chatting below. Type 'quit', 'exit', or 'q' to reset.")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

def run_turn(user_message: str):
    st.session_state.messages.append({"role": "user", "content": user_message})
    state = {"messages": st.session_state.messages}
    
    # Add the required configurable keys for the checkpointer
    config_keys = {
        "thread_id": st.session_state.thread_id,
        "checkpoint_ns": "streamlit_chat",  # Namespace for checkpoints
        "checkpoint_id": str(uuid.uuid4())  # Unique ID for this checkpoint
    }
    
    assistant_response = ""
    try:
        for event in graph.stream(state, config_keys, stream_mode="values"):
            if "messages" in event:
                assistant_message = event["messages"][-1]
                assistant_response = assistant_message.content
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    except Exception as e:
        assistant_response = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    return assistant_response

st.header("Conversation")
for msg in st.session_state.messages:
    st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:")
    submit_button = st.form_submit_button("Send")

if submit_button:
    if user_input.lower() in ["quit", "exit", "q"]:
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())  # Generate new thread ID when conversation is reset
        st.rerun()
    else:
        with st.spinner("Assistant is typing..."):
            run_turn(user_input)
        st.rerun()