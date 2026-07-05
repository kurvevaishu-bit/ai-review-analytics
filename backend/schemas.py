# schemas.py
from pydantic import BaseModel
from typing import Optional, List

class ReviewIn(BaseModel):
    product_id: int
    text: str
    rating: Optional[float] = None

class ReviewOut(BaseModel):
    id: int
    text: str
    rating: Optional[float]
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    lexicon_label: Optional[str]
    lexicon_score: Optional[float]
    topics: Optional[str]

    class Config:
        from_attributes = True

class ProductIn(BaseModel):
    name: str
    category: str
    
        
    