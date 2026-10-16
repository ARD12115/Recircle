"""
Advisor LLM Client - Provider-agnostic with failover, timeout, cache
"""
import hashlib
import json
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class LLMClient:
    """Provider-agnostic LLM client with primary/fallback and caching."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def _cache_key(self, messages: list, model: str, temperature: float) -> str:
        """Generate cache key from request."""
        content = json.dumps({"messages": messages, "model": model, "temperature": temperature}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def chat_completion(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        use_cache: bool = True,
    ) -> Optional[str]:
        """
        Call LLM with primary provider, fallback on failure.
        Returns response content or None if both fail.
        """
        # Check cache
        cache_key = self._cache_key(messages, model or settings.LLM_PRIMARY_MODEL, temperature)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try primary
        result = await self._call_provider(
            provider=settings.LLM_PRIMARY_PROVIDER,
            model=model or settings.LLM_PRIMARY_MODEL,
            api_key=settings.LLM_PRIMARY_API_KEY,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        if result:
            if use_cache:
                self._cache[cache_key] = result
            return result
        
        # Fallback
        print(f"Primary LLM failed, trying fallback: {settings.LLM_FALLBACK_PROVIDER}")
        result = await self._call_provider(
            provider=settings.LLM_FALLBACK_PROVIDER,
            model=settings.LLM_FALLBACK_MODEL,
            api_key=settings.LLM_FALLBACK_API_KEY,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        if result and use_cache:
            self._cache[cache_key] = result
        
        return result
    
    async def _call_provider(
        self,
        provider: str,
        model: str,
        api_key: str,
        messages: list,
        temperature: float,
        max_tokens: int,
    ) -> Optional[str]:
        """Call a specific LLM provider."""
        if not api_key:
            return None
        
        try:
            if provider == "openai":
                return await self._call_openai(model, api_key, messages, temperature, max_tokens)
            elif provider == "anthropic":
                return await self._call_anthropic(model, api_key, messages, temperature, max_tokens)
        except Exception as e:
            print(f"LLM call failed ({provider}): {e}")
            return None
        
        return None
    
    async def _call_openai(self, model: str, api_key: str, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """Call OpenAI-compatible API (supports NVIDIA NIM)."""
        base_url = getattr(settings, 'LLM_PRIMARY_BASE_URL', 'https://api.openai.com/v1')
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            
            if response.status_code != 200:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, model: str, api_key: str, messages: list, temperature: float, max_tokens: int) -> Optional[str]:
        """Call Anthropic API."""
        # Convert messages format
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "system": system_msg,
                    "messages": user_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            
            if response.status_code != 200:
                print(f"Anthropic API error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            return data["content"][0]["text"]
    
    def clear_cache(self):
        """Clear response cache."""
        self._cache.clear()


# Global instance
llm_client = LLMClient()