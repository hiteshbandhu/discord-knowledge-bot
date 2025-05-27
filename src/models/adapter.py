# models/adapter.py
from abc import ABC, abstractmethod
from models.database import ExtractedContent

class ContentAdapter(ABC):
    @classmethod
    @abstractmethod
    def extract(cls, input_data: str) -> ExtractedContent:
        """
        Extract structured content and return it as an ExtractedContent object.
        """
        pass
