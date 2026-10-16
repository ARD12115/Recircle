"""
Vision Fallback - Low confidence path (zero-shot / vision LLM)
"""
import os
import json
import httpx
from typing import Optional, List, Tuple
from PIL import Image
from app.core.config import settings


async def zero_shot_classify(image: Image.Image) -> Optional[Tuple[str, str, float, List[Tuple[str, float]]]]:
    """
    Fallback classification using a vision LLM (e.g., GPT-4V, Claude Vision).
    Returns (predicted_class, subtype, confidence, top3) or None if unavailable.
    """
    # Check if fallback provider is configured
    if not settings.LLM_FALLBACK_API_KEY:
        return None
    
    # Convert image to base64
    import base64
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    prompt = """Classify this waste item into ONE of these 5 categories:
1. recyclable (paper, cardboard, plastic, metal, glass)
2. reusable (clothes, shoes, textiles)
3. biodegradable (food waste, organic)
4. hazardous (batteries, electronics, chemicals)
5. residual (mixed, non-recyclable trash)

Respond with JSON only:
{
  "class": "category_name",
  "subtype": "specific_material",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}"""
    
    try:
        if settings.LLM_FALLBACK_PROVIDER == "openai":
            return await _openai_vision_classify(img_b64, prompt)
        elif settings.LLM_FALLBACK_PROVIDER == "anthropic":
            return await _anthropic_vision_classify(img_b64, prompt)
    except Exception as e:
        print(f"Vision fallback failed: {e}")
        return None
    
    return None


async def _openai_vision_classify(img_b64: str, prompt: str) -> Optional[Tuple[str, str, float, List[Tuple[str, float]]]]:
    """Call OpenAI Vision API."""
    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.LLM_FALLBACK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_FALLBACK_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a waste classification expert."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                        ],
                    },
                ],
                "max_tokens": 200,
                "temperature": 0.1,
            },
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)
        
        predicted_class = result["class"]
        subtype = result["subtype"]
        confidence = result["confidence"]
        
        # Create top3 (only have one prediction from vision LLM)
        top3 = [(predicted_class, confidence)]
        
        return predicted_class, subtype, confidence, top3


async def _anthropic_vision_classify(img_b64: str, prompt: str) -> Optional[Tuple[str, str, float, List[Tuple[str, float]]]]:
    """Call Anthropic Claude Vision API."""
    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.LLM_FALLBACK_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_FALLBACK_MODEL,
                "max_tokens": 200,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                        ],
                    }
                ],
            },
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        content = data["content"][0]["text"]
        result = json.loads(content)
        
        predicted_class = result["class"]
        subtype = result["subtype"]
        confidence = result["confidence"]
        top3 = [(predicted_class, confidence)]
        
        return predicted_class, subtype, confidence, top3


def unsure_response(hazardous_prob: float = 0.0) -> dict:
    """
    Generate 'unsure' response with cautious default.
    If hazardous_prob > 0.20, advise not to put in general bin.
    """
    if hazardous_prob > 0.20:
        return {
            "predicted_class": "unsure",
            "subtype": "unknown",
            "confidence": 0.0,
            "top3": [],
            "guidance": {
                "bin": "Do not put in general bin",
                "steps": [
                    "Item could not be confidently classified",
                    "Hazardous material is possible",
                    "Hand to facility staff for safe disposal",
                ],
                "why": "Model uncertainty with plausible hazardous content",
                "twin_effect": {"node": None, "contamination_delta": 0.0},
            },
            "latency_ms": 0,
        }
    
    return {
        "predicted_class": "unsure",
        "subtype": "unknown",
        "confidence": 0.0,
        "top3": [],
        "guidance": {
            "bin": "Unsure - try retaking photo",
            "steps": [
                "Ensure good lighting and clear background",
                "Center the item in frame",
                "Retake photo or try file upload",
            ],
            "why": "Model confidence below threshold",
            "twin_effect": {"node": None, "contamination_delta": 0.0},
        },
        "latency_ms": 0,
    }