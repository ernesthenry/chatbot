# The Chatbot

The chatbot is a conversational chatbot built using [LangGraph](https://github.com/langchain-ai/langgraph) and Streamlit. It integrates an Anthropic LLM (Claude 3.5) with a web search tool (Tavily) and maintains conversation state using LangGraph's memory checkpointing. This project serves as a starting point for building more advanced, stateful, multi-turn conversational agents.

## Features

- **LLM-Powered Chat:** Leverages Anthropic's Claude model to generate responses.
- **Tool Integration:** Uses Tavily search to fetch up-to-date information when needed.
- **State Management:** Maintains conversation context with LangGraph’s memory checkpointing.
- **Streamlit UI:** Provides an interactive web interface for chatting.
- **Easy Deployment:** Ready-to-use setup for local testing and deployment on platforms like Streamlit Cloud.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/chatbot.git
   cd chatbot
