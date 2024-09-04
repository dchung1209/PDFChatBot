print("start...")

import streamlit as st

st.title('Emotional Chat Bot')

if "counter" not in st.session_state:
    st.session_state.counter = 0

prompt = st.chat_input('Enter your message here:')
if prompt:
    with st.chat_message("You"):
        st.write(prompt)
    
    with st.spinner('Processing...'):
        st.session_state.counter += 1
    
    with st.chat_message("Bot"):
        st.write(f"Hello! You have sent {st.session_state.counter} messages so far.")

print("end...")