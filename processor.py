import streamlit as st
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from qdrant_client import QdrantClient

def create_db():
    API_ENDPOINT = ""
    ASTRA_TOKENS = ""
    ASTRA_NAMESPACE = ""

    # VectorStore : AstraDB
    astra_db = AstraDBVectorStore(
        token = ASTRA_TOKENS,
        api_endpoint = API_ENDPOINT,
        namespace = ASTRA_NAMESPACE,
        collection_name = "pdfchat",
        embedding_dimension = 1536
    )

    return astra_db

def parse_pdf(file, llama_api_key):

    # Parser (PDF reader) : LlamaParse
    parser = LlamaParse(
        api_key = llama_api_key,
        result_type = "markdown",
        num_workers=4,
        language="en"
    )

    return parser.load_data(file)


def create_llm():
    return OpenAI(model="gpt-3.5-turbo")

def create_embed_model():
    return OpenAIEmbedding(model="text-embedding-3-small")

def build_index(documents):
    node_parser = MarkdownElementNodeParser(
        llm=OpenAI(model="gpt-3.5-turbo"), 
        num_workers=8
    )

    nodes = node_parser.get_nodes_from_documents(documents)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    storage_context = StorageContext.from_defaults(
        vector_store = create_db()
    )

    recursive_index = VectorStoreIndex(
        base_nodes + objects, storage_context = storage_context
    )

    return recursive_index

    

    