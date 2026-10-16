"""
Scan Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class WasteClass(str, enum.Enum):
    RECYCLABLE = "recyclable"
    REUSABLE = "reusable"
    BIODEGRADABLE = "biodegradable"
    HAZARDOUS = "hazardous"
    RESIDUAL = "residual"


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    predicted_class = Column(SQLEnum(WasteClass), nullable=False)
    subtype = Column(String(50))
    confidence = Column(Float, nullable=False)
    top3 = Column(Text)  # JSON string
    source_node_id = Column(Integer, ForeignKey("twin_nodes.id"), nullable=True)
    confirmed_bin = Column(String(100), nullable=True)
    image_ref = Column(String(255), nullable=True)
    latency_ms = Column(Integer)
    
    user = relationship("User", backref="scans")
    source_node = relationship("TwinNode", backref="scans")