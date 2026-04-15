# 🎭 Emoji-Only Story Challenge Agent

An interactive, AI-powered guessing game built with Streamlit, LangGraph, and ChatGroq!

## Features
- **Emoji Story Generator:** AI creates beautiful stories using only emojis!
- **Evaluation Engine:** Sophisticated natural language evaluation to determine if your guess is correct.
- **Dynamic Reveal:** The AI clearly explains the story alongside your evaluation.
- **Memory Tracking:** History and scoring are tracked persistently across rounds via LangGraph `MemorySaver`.

## Prerequisites
- Python 3.9+
- A Groq API Key (Get one from [Groq Console](https://console.groq.com/))

## Setup
1. Clone the repository and navigate into it.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your API key:
   ```bash
   cp .env.example .env
   ```
4. Run the application:
   ```bash
   cd emoji_story_agent
   streamlit run app.py
   ```

## Architecture
- **Frontend:** Streamlit 
- **Agent Framework:** LangGraph 
- **LLM:** ChatGroq (`llama-3.3-70b-versatile`)
