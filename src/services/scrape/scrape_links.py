from adapters.scrapers.firecrawl_adapter import FirecrawlAdapter
from adapters.scrapers.images import ImageAdapter
from adapters.scrapers.youtube import YouTubeAdapter
from models.database import ExtractedContent
from typing import Literal

ADAPTERS = {
    "link": FirecrawlAdapter,
    "image": ImageAdapter,
    "youtube": YouTubeAdapter,
}

ScraperType = Literal["link", "image", "youtube"]

def scrape(scraper_type: ScraperType, url: str) -> ExtractedContent :
    adapter = ADAPTERS.get(scraper_type)
    if not adapter:
        raise ValueError(f"Unknown scraper type: {scraper_type}")
    result = adapter.extract(url)
    return result

