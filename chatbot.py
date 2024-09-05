import streamlit as st
import os
import nest_asyncio
from llama_parse import LlamaParse
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from io import BytesIO
from tempfile import NamedTemporaryFile

nest_asyncio.apply()


os.environ["OPENAI_API_KEY"] = ""
os.environ["LLAMA_CLOUD_API_KEY"] = ""

parser = LlamaParse(
    use_vendor_multimodal_model=True,
    vendor_multimodal_model_name="openai-gpt4o",
    vendor_multimodal_api_key=os.environ["OPENAI_API_KEY"],
    num_workers=4,
    language="en"
)


def main():
    st.title('PDF ChatBot by dchung')
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is not None:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
        
        documents = parser.load_data(tmp_file.name)
        st.write("Processing...")
        print(documents)
        os.remove(tmp_file.name)



if __name__ == '__main__':
    main()




