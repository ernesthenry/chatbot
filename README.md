# The Chatbot

The Chatbot is a conversational agent built using [LangGraph](https://github.com/langchain-ai/langgraph) and Streamlit. It integrates an Anthropic LLM (Claude 3.5) with a web search tool (Tavily) and maintains conversation state using LangGraph's memory checkpointing. This project serves as a starting point for building more advanced, stateful, multi-turn conversational agents.

## Features

- **LLM-Powered Chat:** Leverages Anthropic's Claude model to generate responses.
- **Tool Integration:** Uses Tavily search to fetch up-to-date information when needed.
- **State Management:** Maintains conversation context with LangGraph’s memory checkpointing.
- **Streamlit UI:** Provides an interactive web interface for chatting.
- **Easy Deployment:** Ready-to-use setup for local testing and deployment on platforms like Streamlit Cloud.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chatbot.git
cd chatbot
```

### 2. Project Structure

```
chatbot/
├── app.py             # Main Streamlit application file
├── requirements.txt   # Project dependencies
├── README.md          # This file
└── .gitignore         # Files/directories to ignore in Git
```

### 3. Set Up a Virtual Environment

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

Make sure your virtual environment is activated, then run:

```bash
pip install -r requirements.txt
```

## Configuration

The application requires API keys for Anthropic and Tavily. You can set these as environment variables or use a `.env` file. For example, create a `.env` file with:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Alternatively, set them in your shell or via Streamlit secrets if deploying on Streamlit Cloud.

## Usage

To run the chatbot locally, execute:

```bash
streamlit run app.py
```

Open the URL provided by Streamlit (typically [http://localhost:8501](http://localhost:8501)) in your browser and start chatting!

## Deployment

To deploy The Chatbot on Streamlit Cloud:

1. Push your project to GitHub.
2. Create a new app on [Streamlit Cloud](https://share.streamlit.io/) and link your repository.
3. Set your API keys in the Streamlit secrets management.

## Contributing

Contributions are welcome! Please open issues or submit pull requests with improvements, additional features, or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).

