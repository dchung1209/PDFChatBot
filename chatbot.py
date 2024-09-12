import csv
import os
import pandas as pd

from tempfile import NamedTemporaryFile
from llama_index.core import Settings
from llama_index.postprocessor.colbert_rerank import ColbertRerank

import streamlit as st

from processor import parse_pdf, create_llm, create_embed_model, build_index

def reset_conversation():
  st.session_state.chat_history = None
  st.session_state.messages = []

def append_conversation_to_csv():
    if "messages" in st.session_state and st.session_state.messages:
        csv_file =  "chat_history.csv"
        is_exist = os.path.isfile(csv_file)

        with st.spinner("Saving conversations..."):
            with open(csv_file, 'a') as f:
                writer = csv.writer(f)
                if not is_exist:
                    writer.writerow(["Role", "Content"])
            
                for message in st.session_state.messages:
                    writer.writerow([
                        message["role"],
                        message["content"]
                    ])
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
    st.subheader("🔥RAG + Recursive Retrieval + Reranker🔥")
    st.markdown("made by Do Chung : github.com/dchung1209")
    st.button('Reset Chat', on_click=reset_conversation)

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

        try:
            chat_df = pd.read_csv("./chat_history.csv")
        except FileNotFoundError:
            chat_df = pd.DataFrame(columns=["Role", "Content"])
        
        st.write(chat_df)


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


    if prompt := st.chat_input("Ask a question about your document here"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Generating response..."):
            try:
                response = create_response(st.session_state.conversation, prompt)
            except:
                st.markdown("Unexpected error occured")

            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
