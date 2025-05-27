# utils/detect_link_type.py

from urllib.parse import urlparse

def detect_scraper_type(url: str) -> str:
    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif url.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
        return "image"
    elif "cdn.discordapp.com" in url:  # Discord image
        return "image"
    else:
        return "link"
