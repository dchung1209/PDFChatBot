import streamlit as st
import os
import nest_asyncio
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import MarkdownElementNodeParser
from langchain_openai import OpenAIEmbeddings
from processor import parse_pdf, create_llm, create_embed_model, build_index
from tempfile import NamedTemporaryFile
from llama_index.postprocessor.colbert_rerank import ColbertRerank

nest_asyncio.apply()

def reset_conversation():
  st.session_state.chat_history = None
  st.session_state.messages = []

def set_os_env(openai_api_key, llama_api_key):
    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_api_key

def set_llm():
    Settings.llm = create_llm()

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


os.environ["OPENAI_API_KEY"] =""
os.environ["LLAMA_CLOUD_API_KEY"] = ""

def main():
    st.title("PDF Chat Assistant")
    st.subheader("🔥RAG + Recursive Retrieval + Reranker🔥")
    st.markdown("made by Do Chung : github.com/dchung1209")
    st.button('Reset Chat', on_click=reset_conversation)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    llama_api_key = st.sidebar.text_input("Llama API Key", type="password")

    with st.sidebar:
        st.title(
            "Upload your PDF"
        )

        uploaded_file = st.file_uploader(
            "Upload your PDF to get started!", type=["pdf"]
        )


        if uploaded_file is not None:
            if st.button("Process"):
                st.switch_page
                try:
                    st.spinner("Processing...")
                    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                    
                    documents = parse_pdf(tmp_file.name, os.environ["LLAMA_CLOUD_API_KEY"])
                    set_llm()
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
