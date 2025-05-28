# src/tests/test_chroma.py

from database.chroma_db import collection

def test_chroma_search():
    results = collection.get()
    print(results)

if __name__ == "__main__":
    test_chroma_search()