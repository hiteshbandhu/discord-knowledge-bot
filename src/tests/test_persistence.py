from models.database import ExtractedContent
from services.persist.persist_to_db import persist_to_db
from database.chroma_db import query_document, add_document
from database.pg_database import get_by_url

sample_docs = [
    ExtractedContent(
        url="https://example.com/ai",
        title="Intro to AI",
        summary="Overview of Artificial Intelligence.",
        content="AI refers to machines mimicking human intelligence.",
        media_type="link",
        metadata={"topic": "AI"}
    ),
    ExtractedContent(
        url="https://example.com/ml",
        title="Machine Learning 101",
        summary="Basics of ML algorithms.",
        content="ML is a subset of AI that learns from data.",
        media_type="link",
        metadata={"topic": "Machine Learning"}
    ),
    ExtractedContent(
        url="https://example.com/nlp",
        title="NLP Overview",
        summary="Natural Language Processing explained.",
        content="NLP helps machines understand human language.",
        media_type="link",
        metadata={"topic": "NLP"}
    ),
    ExtractedContent(
        url="https://example.com/ds",
        title="Data Science Insights",
        summary="Working with data to extract knowledge.",
        content="Data Science is a combination of statistics and computing.",
        media_type="link",
        metadata={"topic": "Data Science"}
    ),
    ExtractedContent(
        url="https://example.com/dl",
        title="Deep Learning Intro",
        summary="Neural networks and deep learning.",
        content="DL is a set of ML methods based on neural nets.",
        media_type="link",
        metadata={"topic": "Deep Learning"}
    ),
]

def run_test():
    print("🔁 Saving and verifying documents...\n")
    for doc in sample_docs:
        msg = persist_to_db(doc)
        print(f"{doc.url} → {msg}")
        neon_row = get_by_url(doc.url)
        assert neon_row is not None, f"❌ {doc.url} was not saved to Neon!"
        print(f"✅ Found in Neon DB: {doc.url}")

    print("\n🔍 Querying ChromaDB for: 'neural networks'\n")
    results = query_document(query_text="neural networks", n_results=3)

    docs = results["documents"][0]
    for i, text in enumerate(docs):
        print(f"{i+1}. {text}")

    assert any("neural nets" in doc.lower() for doc in docs), "❌ Expected Deep Learning content not found!"

    print("\n✅ Test passed: ChromaDB returned semantically relevant result.\n")

if __name__ == "__main__":
    run_test()
