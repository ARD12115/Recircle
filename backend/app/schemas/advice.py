"""
Advice Schemas - Request/Response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Action(BaseModel):
    title: str
    why: str
    expected_impact: str
    effort: Literal["low", "medium", "high"]
    owner: str


class AdviceResponse(BaseModel):
    summary: str
    issues: List[str]
    actions: List[Action]
    reuse_ideas: List[str]
    disclaimer: str
    cached: bool = False
    provider: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    message: ChatMessage