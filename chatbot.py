import streamlit as st
import os
import nest_asyncio
from llama_parse import LlamaParse
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from langchain.text_splitter import MarkdownTextSplitter
from langchain_openai import OpenAIEmbeddings


from io import BytesIO
from tempfile import NamedTemporaryFile

nest_asyncio.apply()

def set_os_env(openai_api_key, llama_api_key):
    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["LLAMA_CLOUD_API_KEY"] = llama_api_key

os.environ["OPENAI_API_KEY"] =""
os.environ["LLAMA_CLOUD_API_KEY"] = ""

Settings.llm = 
Settings.tokenizer = 
Settings.embed_model = OpenAIEmbeddings(
        api_key=os.environ["OPENAI_API_KEY"],
        model = "text-embedding-3-small")

def pdf_to_md(file, llama_api_key):
    parser = LlamaParse(
        api_key = llama_api_key,
        result_type = "markdown",
        num_workers=4,
        language="en"
    )
    return parser.load_data(file)

def embeded_text(documents):
    #Chunking
    markdown_splitter = MarkdownTextSplitter(chunk_size=256, chunk_overlap=0)
    docs = markdown_splitter.create_documents(documents)
    embeddings_model = OpenAIEmbeddings(
        api_key=os.environ["OPENAI_API_KEY"],
        model = "text-embedding-3-small")
    embeddings = embeddings_model.embed(docs)
    return embeddings



def main():
    st.title('PDF ChatBot by dchung')
    """openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    llama_api_key = st.sidebar.text_input("Llama API Key", type="password")"""

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is not None:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
        
        documents = pdf_to_md(tmp_file.name, os.environ["LLAMA_CLOUD_API_KEY"])
        st.write("Successfully procsessed✅")
        embeded_text(documents)
        os.remove(tmp_file.name)



if __name__ == '__main__':
    main()




