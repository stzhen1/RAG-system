from typing import List, Dict, AsyncGenerator
from app.adapters.base import LLMProvider
from app.config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model

    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key)
        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model

    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=self.api_key)

        system = None
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        kwargs.pop("temperature", None)
        async with client.messages.stream(
            model=self.model,
            system=system,
            messages=user_messages,
            max_tokens=kwargs.pop("max_tokens", 4096),
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or settings.ollama_model
        self.base_url = base_url or settings.ollama_base_url

    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        import httpx
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]


def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider
    if provider == "openai":
        return OpenAIProvider()
    elif provider == "anthropic":
        return AnthropicProvider()
    elif provider == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
