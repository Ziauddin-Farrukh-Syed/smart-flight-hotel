from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv(ENV_FILE)

print(f"Project root: {PROJECT_ROOT}")
print(f".env file: {ENV_FILE}")
print(f".env exists: {ENV_FILE.exists()}")


# ---------------------------------------------------------
# Load knowledge documents
# ---------------------------------------------------------

def load_knowledge_documents() -> list[Document]:

    print(f"Knowledge directory: {KNOWLEDGE_DIR}")

    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge directory does not exist: {KNOWLEDGE_DIR}"
        )

    documents = []

    files = list(KNOWLEDGE_DIR.glob("*.txt"))

    print(f"Found {len(files)} knowledge files")

    for file_path in files:

        print(f"Loading: {file_path.name}")

        text = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name
                },
            )
        )

    return documents


# ---------------------------------------------------------
# Build vector store
# ---------------------------------------------------------

def build_vector_store():

    documents = load_knowledge_documents()

    if not documents:
        raise ValueError(
            "No knowledge documents were found."
        )

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} document chunks")

    # Create embeddings
    print("Creating OpenAI embeddings...")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    # Make sure vector-store directory exists
    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create Chroma vector database
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
        collection_name="travel_knowledge",
    )

    print(
        f"Vector store created at: {VECTOR_STORE_DIR}"
    )

    print(
        f"Stored {len(chunks)} chunks"
    )

    return vector_store


# ---------------------------------------------------------
# Run ingestion
# ---------------------------------------------------------

if __name__ == "__main__":

    build_vector_store()

    print()
    print("RAG knowledge base created successfully.")