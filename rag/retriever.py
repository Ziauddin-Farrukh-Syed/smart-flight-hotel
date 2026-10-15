from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Get vector store
# ---------------------------------------------------------

def get_vector_store():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = Chroma(
        collection_name="travel_knowledge",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    return vector_store


# ---------------------------------------------------------
# Search knowledge
# ---------------------------------------------------------

def search_knowledge(
    query: str,
    k: int = 3,
):

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query,
        k=k,
    )

    return documents


# ---------------------------------------------------------
# Build context
# ---------------------------------------------------------

def get_knowledge_context(
    query: str,
    k: int = 3,
) -> str:

    documents = search_knowledge(
        query=query,
        k=k,
    )

    if not documents:
        return "No relevant travel knowledge was found."

    context_parts = []

    for document in documents:

        source = document.metadata.get(
            "source",
            "unknown"
        )

        context_parts.append(
            f"SOURCE: {source}\n"
            f"{document.page_content}"
        )

    return "\n\n---\n\n".join(
        context_parts
    )


