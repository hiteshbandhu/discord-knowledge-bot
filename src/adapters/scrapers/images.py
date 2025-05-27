# adapters/scrapers/images.py

import requests
from models.adapter import ContentAdapter
from models.database import ExtractedContent
from services.llm.gemini import describe_image
    
class ImageAdapter(ContentAdapter):
    @classmethod
    def extract(cls, image_url: str) -> ExtractedContent:
        # Download image bytes
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = response.content

        # Get description and OCR from Gemini
        description = describe_image(image_bytes)

        return ExtractedContent(
            source="image",
            url=image_url,
            title=None,
            summary=None,
            content=description,
            tags=[],
            media_type="image",
            metadata={"source": "gemini-vision"}
        )
