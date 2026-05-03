import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.call_center.intake_agent import IntakeAgent
from app.agents.call_center.transcription_agent import TranscriptionAgent
from app.agents.call_center.summarization_agent import SummarizationAgent
from app.agents.call_center.quality_score_agent import QualityScoreAgent
from app.agents.call_center.schemas import AnalyzeCallRequest, CallInputType


@pytest.mark.asyncio
async def test_intake_agent_requires_transcript_or_audio():
    intake = IntakeAgent()
    with pytest.raises(ValueError):
        await intake.run(AnalyzeCallRequest(session_id="sess-1"))


@pytest.mark.asyncio
async def test_intake_agent_detects_transcript_input():
    intake = IntakeAgent()
    result = await intake.run(
        AnalyzeCallRequest(
            session_id="sess-2",
            transcript="Customer asked for refund and billing clarification.",
        )
    )

    assert result.input_type == CallInputType.TRANSCRIPT
    assert result.has_audio is False
    assert result.transcript_word_count > 0


@pytest.mark.asyncio
async def test_transcription_agent_uses_provided_transcript_without_audio_call(monkeypatch):
    agent = TranscriptionAgent(api_key="test-key")

    called = False

    async def fake_create(*args, **kwargs):
        nonlocal called
        called = True
        return None

    monkeypatch.setattr(agent.client.audio.transcriptions, "create", fake_create)

    result = await agent.run(
        AnalyzeCallRequest(
            session_id="sess-3",
            transcript="This transcript should pass through unchanged.",
        )
    )

    assert called is False
    assert result.transcript == "This transcript should pass through unchanged."
    assert result.source == "provided_transcript"


@pytest.mark.asyncio
async def test_transcription_agent_requires_audio_when_no_transcript():
    agent = TranscriptionAgent(api_key="test-key")

    with pytest.raises(ValueError):
        await agent.run(AnalyzeCallRequest(session_id="sess-4"))


@pytest.mark.asyncio
async def test_summarization_agent_fallback_on_bad_json():
    with patch("app.agents.call_center.summarization_agent.ChatOpenAI") as mock_chat_openai:
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="invalid-json"))
        mock_chat_openai.return_value = mock_llm
        agent = SummarizationAgent(api_key="test-key")
        result = await agent.run("Customer asked for invoice clarification")

    assert "unavailable" in result.summary.lower()
    assert "fallback" in result.tags


@pytest.mark.asyncio
async def test_quality_agent_clamps_values_and_fallback_on_bad_fields():
    with patch("app.agents.call_center.quality_score_agent.ChatOpenAI") as mock_chat_openai:
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(
                content='{"tone_score": 2, "empathy_score": -1, "professionalism_score": "x", "resolution_score": 0.7, "overall_score": 1.5, "compliance_flags": "missing_disclaimer"}'
            )
        )
        mock_chat_openai.return_value = mock_llm
        agent = QualityScoreAgent(api_key="test-key")
        result = await agent.run("Call transcript")

    assert result.tone_score == 1.0
    assert result.empathy_score == 0.0
    assert result.professionalism_score == 0.0
    assert result.resolution_score == 0.7
    assert result.overall_score == 1.0
    assert result.compliance_flags == ["missing_disclaimer"]
