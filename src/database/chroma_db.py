import chromadb
from chromadb.utils import embedding_functions

default_ef = embedding_functions.DefaultEmbeddingFunction()

# Initialize ChromaDB client with persistence
client = chromadb.PersistentClient(path="_data/vector_data_chroma")

# Create or get collection
collection = client.get_or_create_collection(name="scraped_content")

def add_document(doc_id: str, content: str, metadata: dict):
    try:
        collection.add(documents=[content], metadatas=[metadata], ids=[doc_id])
        print(f"ChromaDB: Added doc_id={doc_id}")
    except Exception as e:
        print(f"ChromaDB ERROR for doc_id={doc_id}: {e}")

def query_document(query_text: str, n_results: int = 4):
    return collection.query(query_texts=[query_text], n_results=n_results)
