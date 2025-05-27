# tests/test_adapters.py

import sys
sys.path.append("src")  # Ensure the src/ folder is on the path

from adapters.scrapers.firecrawl import FirecrawlAdapter
from adapters.scrapers.youtube import YouTubeAdapter
from adapters.scrapers.images import ImageAdapter

def test_firecrawl():
    url = "https://langchain.com"
    result = FirecrawlAdapter.extract(url)
    print("\n--- Firecrawl Result ---")
    print(result.model_dump_json(indent=2))

def test_youtube():
    url = "https://youtu.be/dQw4w9WgXcQ"
    result = YouTubeAdapter.extract(url)
    print("\n--- YouTube Result ---")
    print(result.model_dump_json(indent=2))

def test_image():
    url = "https://images.unsplash.com/photo-1748183781742-a2473d27a763?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"  # Replace with real one
    result = ImageAdapter.extract(url)
    print("\n--- Image Result ---")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    # Run only the ones you want to test:
    test_firecrawl()
    test_youtube()
    test_image()
