# adapters/scrapers/firecrawl.py

from firecrawl import FirecrawlApp
from models.adapter import ContentAdapter
from models.database import ExtractedContent
from services.llm.gemini import summarize_text
from dotenv import load_dotenv
load_dotenv()
import os

class FirecrawlAdapter(ContentAdapter):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    @classmethod
    def extract(cls, url: str) -> ExtractedContent:
        try:
            result = cls.app.scrape_url(url, formats=["markdown", "html"])
            metadata = result.metadata or {}
            content = result.markdown or result.html
            summary = summarize_text(content) if content else None

            return ExtractedContent(
                url=metadata.get("sourceURL", url),
                title=metadata.get("title"),
                summary=summary,
                content=content,
                tags=metadata.get("keywords", "").split(",") if metadata.get("keywords") else [],
                media_type="link",
                metadata={"source": "firecrawl"}
            )

        except Exception as e:
            raise RuntimeError(f"Firecrawl scraping failed for {url}: {e}")
