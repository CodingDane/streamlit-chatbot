import requests
import streamlit as st
import os
import json

load_dotenv()

dify_api_key = st.secrets('DIFY_API_KEY')

url = 'https://api.dify.ai/v1/chat-messages'

st.title('カラスのお悩み相談室')

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

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
        headers = {
            'Authorization': f'Bearer {dify_api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            "inputs": {},
            "query": prompt,
            "response_mode": "streaming",
            "conversation_id": st.session_state.conversation_id,
            "user": "alex-123",
            "files": []
        }
        response =  requests.post(url, headers=headers, json=payload, stream=True)

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    json_data = line[len("data: "):]
                    try:
                        parsed_data = json.loads(json_data)
                        if "event" in parsed_data and parsed_data["event"] == "node_finished":
                            delta_content = parsed_data["data"].get("outputs", {}).get("answer", "")
                            full_response += delta_content
                            message_placeholder.markdown(full_response + "...")
                        if "conversation_id" in parsed_data:
                            st.session_state.conversation_id = parsed_data["conversation_id"]
                    except json.JSONDecodeError:
                        continue
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
