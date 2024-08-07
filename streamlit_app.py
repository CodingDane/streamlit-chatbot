import openai
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if "openai_chatbot" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

st.title('カラスのお悩み相談室')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("カラスに何か質問してみよう")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
               {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
          ],
          stream=True,
        ):
          delta_content = response.choices[0].delta.content or ""
          if delta_content is not None:
              full_response += delta_content
          message_placeholder.markdown(full_response + "...")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
