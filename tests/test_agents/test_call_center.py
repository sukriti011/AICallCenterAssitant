import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.call_center.agent import CallCenterAgent
from app.agents.call_center.schemas import CallCenterRequest, Intent


@pytest.fixture
def agent():
    with patch("app.agents.call_center.agent.get_settings") as mock_settings:
        mock_settings.return_value.openai_api_key = "test-key"
        # Each ChatOpenAI() call must return a distinct mock so llm != intent_llm
        with patch("app.agents.call_center.agent.ChatOpenAI", side_effect=lambda **_: MagicMock()):
            return CallCenterAgent()


@pytest.mark.asyncio
async def test_classify_intent_billing(agent):
    mock_response = MagicMock()
    mock_response.content = '{"intent": "billing", "confidence": 0.95, "escalate": false, "suggested_actions": ["Check invoice"]}'
    agent.intent_llm.ainvoke = AsyncMock(return_value=mock_response)

    result = await agent.classify_intent("I have a question about my bill")
    assert result["intent"] == "billing"
    assert result["confidence"] == 0.95
    assert result["escalate"] is False


@pytest.mark.asyncio
async def test_classify_intent_fallback_on_bad_json(agent):
    mock_response = MagicMock()
    mock_response.content = "not valid json"
    agent.intent_llm.ainvoke = AsyncMock(return_value=mock_response)

    result = await agent.classify_intent("some message")
    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.0


@pytest.mark.asyncio
async def test_chat_returns_response(agent):
    intent_mock = MagicMock()
    intent_mock.content = '{"intent": "general_inquiry", "confidence": 0.8, "escalate": false, "suggested_actions": ["Browse FAQ"]}'
    agent.intent_llm.ainvoke = AsyncMock(return_value=intent_mock)

    chat_mock = MagicMock()
    chat_mock.content = "Hello! How can I help you today?"
    agent.llm.ainvoke = AsyncMock(return_value=chat_mock)

    request = CallCenterRequest(session_id="sess-001", message="Hi there")
    response = await agent.chat(request)

    assert response.session_id == "sess-001"
    assert response.response == "Hello! How can I help you today?"
    assert response.detected_intent == Intent.GENERAL_INQUIRY
    assert response.escalate is False


@pytest.mark.asyncio
async def test_chat_persists_history(agent):
    for mock_llm in [agent.intent_llm, agent.llm]:
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content='{"intent":"general_inquiry","confidence":0.8,"escalate":false,"suggested_actions":[]}'
        ))
    agent.llm.ainvoke = AsyncMock(return_value=MagicMock(content="Reply 1"))

    req = CallCenterRequest(session_id="sess-history", message="First message")
    await agent.chat(req)

    from app.agents.call_center.agent import _session_store
    assert "sess-history" in _session_store
    messages = _session_store["sess-history"].chat_memory.messages
    assert len(messages) == 2  # human + ai


def test_clear_session(agent):
    from app.agents.call_center.agent import _session_store
    from langchain.memory import ConversationBufferWindowMemory
    _session_store["to-clear"] = ConversationBufferWindowMemory(return_messages=True, memory_key="chat_history")

    assert agent.clear_session("to-clear") is True
    assert "to-clear" not in _session_store
    assert agent.clear_session("nonexistent") is False
