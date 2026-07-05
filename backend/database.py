# database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'reviews.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    reviews = relationship("Review", back_populates="product")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    text = Column(Text)
    rating = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    lexicon_label = Column(String, nullable=True)
    lexicon_score = Column(Float, nullable=True)
    topics = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="reviews")

def init_db():
    Base.metadata.create_all(bind=engine)
    
    