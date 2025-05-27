# adapters/scrapers/youtube.py

from models.adapter import ContentAdapter
from models.database import ExtractedContent
from services.llm.gemini import summarize_youtube_video

class YouTubeAdapter(ContentAdapter):
    @classmethod
    def extract(cls, url: str) -> ExtractedContent:
        summary = summarize_youtube_video(url)
        
        return ExtractedContent(
            source="youtube",
            url=url,
            title=None,                  # Gemini doesn’t return this yet
            summary=summary,
            content=None,                # Not needed
            tags=[],
            media_type="youtube",
            metadata={"source": "gemini-vision"}
        )
