import pytest
from unittest.mock import AsyncMock, patch
from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_chat_service_builds_prompt_with_context():
    service = ChatService()

    with patch.object(service.retrieval_service, 'retrieve_context', new_callable=AsyncMock) as mock_retrieve, \
         patch.object(service.llm_provider, 'chat_stream', new_callable=AsyncMock) as mock_llm:

        mock_retrieve.return_value = "Relevant document context here."
        mock_llm.return_value = iter(["Response ", "with ", "citations"])

        history = []
        async for chunk in service.chat("What is RAG?", history, filters={}):
            pass

        mock_retrieve.assert_called_once_with("What is RAG?", filters={}, max_tokens=8000)
        mock_llm.assert_called_once()


@pytest.mark.asyncio
async def test_chat_service_yields_chunks():
    service = ChatService()

    with patch.object(service.retrieval_service, 'retrieve_context', new_callable=AsyncMock) as mock_retrieve, \
         patch.object(service.llm_provider, 'chat_stream', new_callable=AsyncMock) as mock_llm:

        mock_retrieve.return_value = "Context."
        mock_llm.return_value = iter(["Hello", " world"])

        chunks = []
        async for chunk in service.chat("Hi", [], filters={}):
            chunks.append(chunk)

        assert chunks == ["Hello", " world"]


@pytest.mark.asyncio
async def test_chat_service_includes_history():
    service = ChatService()
    history = [
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"},
    ]

    with patch.object(service.retrieval_service, 'retrieve_context', new_callable=AsyncMock) as mock_retrieve, \
         patch.object(service.llm_provider, 'chat_stream', new_callable=AsyncMock) as mock_llm:

        mock_retrieve.return_value = "Context."
        mock_llm.return_value = iter(["Answer"])

        async for _ in service.chat("Follow up", history, filters={}):
            pass

        call_args = mock_llm.call_args[0][0]
        assert len(call_args) >= 3
