# 🤖 Nova AI

An AI chatbot built using Python, Streamlit, and the Google Gemini API.

## Features
- AI-powered conversations with recent-history memory
- Adjustable model, creativity, and remembered-turn settings
- Example prompts for getting started
- Export the current conversation as JSON
- Clear, friendly configuration and request errors

## Technologies
- Python
- Streamlit
- Google Gemini API

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Run the application

```bash
streamlit run app.py
```

## API Key

Create a `.env` file in this directory:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
```

`GEMINI_MODEL` is optional and defaults to `gemini-2.5-flash`. Never upload
your API key to GitHub.

## Usage

Use the sidebar to select the model and tune response creativity. The
remembered-turn setting limits the recent conversation sent to Gemini, which
helps control context size. Use **Export chat** to download the current
conversation as a JSON file.