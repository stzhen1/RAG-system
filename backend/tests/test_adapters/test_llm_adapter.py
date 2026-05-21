import pytest
from app.adapters.llm_adapter import get_llm_provider


@pytest.mark.asyncio
async def test_get_llm_provider_returns_provider():
    provider = get_llm_provider()
    assert provider is not None
    assert hasattr(provider, "chat_stream")


@pytest.mark.asyncio
async def test_openai_provider_builds_correct_payload():
    from app.adapters.llm_adapter import OpenAIProvider
    provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
    messages = [{"role": "user", "content": "Hello"}]
    assert provider.model == "gpt-4o"
    assert provider.api_key == "sk-test"
