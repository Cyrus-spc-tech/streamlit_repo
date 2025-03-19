import streamlit as st
import openai

import time

openai.api_key = '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'

st.header("Chat Bot Demo")

st.caption("This demo app is connected to OpenAI's GPT-3/GPT-4.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        assistant_response = response.choices[0].text.strip()
        
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})