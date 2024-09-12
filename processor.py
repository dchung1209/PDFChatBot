import os

import nest_asyncio
nest_asyncio.apply()

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.astra_db import AstraDBVectorStore
from llama_parse import LlamaParse

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

def parse_pdf(file):

    # Parser (PDF reader) : LlamaParse
    parser = LlamaParse(
        api_key = os.environ.get("LLAMA_CLOUD_API_KEY"),
        result_type = "markdown",
        num_workers=4,
        language="en"
    )

    return parser.load_data(file)


def create_llm(model):
    if (model == "Llama 3.1"):
        return Groq(model="llama-3.1-70b-versatile")
    elif (model =="GPT-4o"):
        return OpenAI(model="gpt-4o")
    else:
        print(f"Unrecognized model: {model}")
        return None

def create_embed_model():
    return OpenAIEmbedding(model="text-embedding-ada-002")

def build_index(documents):
    node_parser = MarkdownElementNodeParser(
        num_workers=8
    )

    nodes = node_parser.get_nodes_from_documents(
        documents
    )

    base_nodes, objects = node_parser.get_nodes_and_objects(
        nodes
    )

    storage_context = StorageContext.from_defaults(
        vector_store = create_db()
    )

    recursive_index = VectorStoreIndex(
        base_nodes + objects, storage_context = storage_context
    )

    return recursive_index

