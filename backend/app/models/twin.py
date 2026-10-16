"""
Digital Twin Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class NodeType(str, enum.Enum):
    SOURCE = "source"
    BIN = "bin"
    COLLECTION = "collection"
    FACILITY = "facility"


class TwinNode(Base):
    __tablename__ = "twin_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(NodeType), nullable=False)
    name = Column(String(100), nullable=False)
    config_json = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TwinEdge(Base):
    __tablename__ = "twin_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, ForeignKey("twin_nodes.id"), nullable=False)
    to_id = Column(Integer, ForeignKey("twin_nodes.id"), nullable=False)
    weight = Column(Float, default=0.0)  # items per tick
    route_prob = Column(Float, default=1.0)  # routing probability
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TwinSnapshot(Base):
    __tablename__ = "twin_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    tick = Column(Integer, nullable=False)
    metrics_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())