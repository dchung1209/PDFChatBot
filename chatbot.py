import os
import pandas as pd

from datetime import datetime
from tempfile import NamedTemporaryFile
from llama_index.core import Settings
from llama_index.postprocessor.colbert_rerank import ColbertRerank

import streamlit as st
import pymysql

from processor import parse_pdf, create_llm, create_embed_model, build_index
from sqlserver import SQLUtils

server = "127.0.0.1" # Container Name
username = "root" # Username
port = 3307 # Port
database = "pdfchat" # Database
password = "" # Password

if 'sql_utils' not in st.session_state:
    st.session_state.sql_utils = SQLUtils(server, username, password, database, port)

def reset_conversation():
  st.session_state.chat_history = None
  st.session_state.messages = []

def append_conversation():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation = st.session_state.messages
    if conversation:
        user_conversation_text = []
        bot_conversation_text = []
        for message in conversation:
            if message["role"] == "user":
                user_conversation_text.append(f"{message["content"]}")
            
            if message["role"] == "assistant":
                bot_conversation_text.append(f"{message["content"]}")
            
        user_conversation = "\n".join(user_conversation_text)
        bot_conversation = "\n".join(bot_conversation_text)
        st.session_state.sql_utils.save_conversation(timestamp, user_conversation, bot_conversation)
        st.write("Conversation saved successfully✅")
    else:
        st.error("No conversation to save")

def set_os_env(open_api_key, groq_api_key, llama_api_key):
    os.environ["OPEN_API_KEY"] = open_api_key
    os.environ["GROQ_API_KEY"] = groq_api_key
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_api_key

def set_llm(model):
    Settings.llm = create_llm(model)

def set_embed_model():
    Settings.embed_model = create_embed_model()

def create_response(index, question):
    #Reranker : colbert
    colbert_reranker = ColbertRerank(
        top_n=5,
        model="colbert-ir/colbertv2.0",
        tokenizer="colbert-ir/colbertv2.0",
        keep_retrieval_score=True,
    )

    recursive_query_engine = index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=[colbert_reranker],
        verbose=True
    )

    response = recursive_query_engine.query(
        question
    )

    return response

os.environ["OPENAI_API_KEY"] = ""
os.environ["LLAMA_CLOUD_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""

def main():
    st.title(":rainbow[PDF] Chat Assistant")
    st.markdown("🔥made by Do Chung : github.com/dchung1209🔥")
    st.button('Save Chat', on_click=append_conversation)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.sidebar:
        llm_model = st.radio(
            "Select your LLM model",
            [ "Llama 3.1", "GPT-4o"],
            captions=[
                "META",
                "OPEN AI",
            ])
        
        groq_api_key = ""
        if (llm_model == "Llama 3.1"):
            groq_api_key = st.text_input("GroqCloud API Key", type="password")

        open_api_key = st.text_input("OpenAI API Key", type="password")
        llama_api_key = st.text_input("LlamaCloud API Key", type="password")
        
        if st.button("Set Keys"):
            try:
                set_os_env(open_api_key, groq_api_key, llama_api_key)
                st.write("Keys set successfully✅")
            except:
                st.error("Invalid Behaviour")
                return
        
        uploaded_file = st.file_uploader(
            "Upload your PDF to get started!", type=["pdf"]
        )


        if uploaded_file is not None:
            if st.button("Process"):
                try:
                    st.spinner("Processing...")
                    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                    
                    documents = parse_pdf(tmp_file.name)
                    set_llm(llm_model)
                    set_embed_model()
                    recursive_index = build_index(documents)

                    st.session_state.conversation = recursive_index
                    st.write("Successfully procsessed✅")

                except:
                    st.error("Invalid Behaviour")
                    return
        
    unique_timestamp = st.session_state.sql_utils.query_timestamp()

    for timestamp, user_messages, bot_messages in zip(unique_timestamp, 
                                                      st.session_state.sql_utils.query_user_content(), 
                                                      st.session_state.sql_utils.query_bot_content()
                                                        ):
        button_label = f"{timestamp[0]}"
        if st.sidebar.button(button_label):
                for user_message, bot_message in zip(user_messages, bot_messages):
                    with st.chat_message("user"):
                        st.markdown(user_message)
                    
                    with st.chat_message("assistant"):
                        st.markdown(bot_message)

    if prompt := st.chat_input("Ask a question about your document here"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Generating response..."):
            try:
                response = create_response(st.session_state.conversation, prompt)
            except:
                response = create_response

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
