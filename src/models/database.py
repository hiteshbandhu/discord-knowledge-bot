# models/database.py
from pydantic import BaseModel
from typing import Optional, List

class ExtractedContent(BaseModel):
    url: str
    title: Optional[str]
    summary: Optional[str]
    content: Optional[str]         # raw extracted text or transcript
    tags: Optional[List[str]] = []
    media_type: str                # "link", "youtube", "image"
    metadata: dict                 # additional info specific to source
