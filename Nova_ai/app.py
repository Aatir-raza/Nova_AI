import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="Nova AI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Nova AI")
st.caption("Your personal AI assistant")

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    st.error("Please configure your API key in the .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Nova AI")
    st.write("Powered by Gemma")
    st.write("Built by Aatir raza ")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.write("Built at Hacktoberfest Hack Day 2026")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask Nova anything...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Nova is thinking..."):
            try:
                conversation = []

                for message in st.session_state.messages:
                    role = (
                        "user"
                        if message["role"] == "user"
                        else "model"
                    )

                    conversation.append({
                        "role": role,
                        "parts": [{"text": message["content"]}]
                    })

                response = client.models.generate_content(
                    model=model,
                    contents=conversation,
                    config={
                        "system_instruction": """
    You are Nova AI, a personal AI assistant created by Aatir Raza,
    a Computer Science Engineering student.

    If anyone asks who built you, who created you, or who your developer is,
    always answer: "I was built by Aatir Raza during Hacktoberfest Hack Day 2026."

    Be helpful, friendly, and accurate.
    """
}
                        )
                    

                answer = response.text or "I could not generate a response."

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error("AI request failed. Check the API configuration.")
                st.caption(str(error))
                