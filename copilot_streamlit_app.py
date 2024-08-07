import requests
from dotenv import load_dotenv
import streamlit as st
import os
import json

load_dotenv()

dify_api_key = os.getenv('COPILOT_API_KEY')

url = 'https://api.dify.ai/v1/chat-messages'

st.title('CITY INSIGHT Copilot DEMO')

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
        response = requests.post(url, headers=headers, json=payload, stream=True)

        # Log the status code and raw response content
        print(f"Status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8').strip()
                print(f"Raw line: {line}")  # Log the raw response line
                if line.startswith("data: "):
                    json_data = line[len("data: "):]
                    try:
                        parsed_data = json.loads(json_data)
                        print(f"Parsed data: {parsed_data}")  # Log the parsed data
                        if "event" in parsed_data:
                            if parsed_data["event"] == "message":
                                delta_content = parsed_data.get("answer", "")
                                full_response += delta_content
                                message_placeholder.markdown(full_response + "...")
                            if parsed_data["event"] == "node_finished":
                                delta_content = parsed_data["data"].get("outputs", {}).get("answer", "")
                                full_response += delta_content
                                message_placeholder.markdown(full_response + "...")
                            if parsed_data["event"] == "message_end":
                                message_placeholder.markdown(full_response)
                            if "conversation_id" in parsed_data:
                                st.session_state.conversation_id = parsed_data["conversation_id"]
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")  # Log JSON decode errors
                        continue
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
