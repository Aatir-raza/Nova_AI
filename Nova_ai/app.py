import json
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

SYSTEM_INSTRUCTION = """
You are Nova AI, a personal AI assistant created by Aatir Raza,
a Computer Science Engineering student.

If anyone asks who built you, who created you, or who your developer is,
always answer: "I was built by Aatir Raza during Hacktoberfest Hack Day 2026."

Be helpful, friendly, concise, and accurate. If you are unsure, say so.
""".strip()

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MAX_HISTORY = 10
EXAMPLE_PROMPTS = (
    "Explain a difficult concept simply",
    "Help me plan my day",
    "Review this idea and suggest improvements",
)

st.set_page_config(
    page_title="Nova AI",
    page_icon="🤖",
    layout="centered",
)


@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    """Create one Gemini client per API key for the lifetime of the app."""
    return genai.Client(api_key=api_key)


def build_conversation(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Convert the UI message format to the format expected by Gemini."""
    return [
        {
            "role": "user" if message["role"] == "user" else "model",
            "parts": [{"text": message["content"]}],
        }
        for message in messages
        if message.get("content", "").strip()
    ]


def generate_answer(
    client: genai.Client,
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
) -> str:
    """Generate a response using the selected conversation settings."""
    response = client.models.generate_content(
        model=model,
        contents=build_conversation(messages),
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": temperature,
        },
    )
    answer = (response.text or "").strip()
    if not answer:
        raise ValueError("The model returned an empty response.")
    return answer


def export_chat(messages: list[dict[str, str]]) -> str:
    """Serialize the current chat in a portable, readable JSON format."""
    return json.dumps(messages, indent=2, ensure_ascii=False)


st.title("🤖 Nova AI")
st.caption("Your personal AI assistant, powered by Google Gemini")

api_key = os.getenv("GEMINI_API_KEY", "").strip()
configured_model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

if not api_key:
    st.error("Nova AI is not configured yet.")
    st.info(
        "Add GEMINI_API_KEY to a local .env file, then restart Streamlit. "
        "Keep this key private and never commit it."
    )
    st.stop()

try:
    client = get_client(api_key)
except Exception:
    st.error("Nova AI could not initialize the Gemini client. Check your API key.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Nova AI")
    st.caption("Built by Aatir Raza")

    model_options = list(dict.fromkeys([configured_model, DEFAULT_MODEL]))
    model = st.selectbox("Model", model_options, index=0)
    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower values are more focused; higher values are more creative.",
    )
    max_history = st.slider(
        "Remembered turns",
        min_value=2,
        max_value=20,
        value=DEFAULT_MAX_HISTORY,
        step=2,
        help="Limits how much recent conversation is sent with each request.",
    )

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.session_state.messages:
        st.download_button(
            "⬇️ Export chat",
            data=export_chat(st.session_state.messages),
            file_name="nova-ai-chat.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    st.caption(f"{len(st.session_state.messages)} messages in this chat")
    st.caption("Built at Hacktoberfest Hack Day 2026")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    st.subheader("Try an example")
    example_columns = st.columns(len(EXAMPLE_PROMPTS))
    for column, example in zip(example_columns, EXAMPLE_PROMPTS):
        if column.button(example, use_container_width=True):
            st.session_state.pending_prompt = example
            st.rerun()

prompt = st.session_state.pop("pending_prompt", None) or st.chat_input(
    "Ask Nova anything..."
)

if prompt and prompt.strip():
    prompt = prompt.strip()
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Nova is thinking..."):
            try:
                recent_messages = st.session_state.messages[-max_history * 2 :]
                answer = generate_answer(
                    client,
                    recent_messages,
                    model,
                    temperature,
                )
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as error:
                st.error("Nova could not complete that request.")
                st.caption(f"{type(error).__name__}: Please verify your model and API key.")
