from pydantic import BaseModel
from typing import Optional

class Recommendation(BaseModel):
    """Model untuk satu item rekomendasi bacaan."""
    title: str
    summary: str
    source: str = "Wikipedia" # Sumber bisa diperluas nanti
    url: Optional[str] = None