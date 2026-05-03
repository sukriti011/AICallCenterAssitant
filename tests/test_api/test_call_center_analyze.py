from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.call_center import get_call_center_agent
from app.agents.call_center.schemas import (
    AnalyzeCallResponse,
    AnalyzeCallRequest,
    CallInputType,
    IntakeResult,
    QualityScoreResult,
    RoutingResult,
    SummaryResult,
)


class FakeCallCenterAgent:
    def __init__(self):
        self.last_request = None

    async def analyze_call(self, request: AnalyzeCallRequest) -> AnalyzeCallResponse:
        self.last_request = request
        transcript = request.transcript or "transcribed from audio"
        return AnalyzeCallResponse(
            session_id=request.session_id,
            transcript=transcript,
            intake=IntakeResult(
                session_id=request.session_id,
                customer_id=request.customer_id,
                input_type=CallInputType.TRANSCRIPT if request.transcript else CallInputType.AUDIO,
                has_audio=bool(request.audio_base64),
                transcript_word_count=len((request.transcript or "").split()),
            ),
            summary=SummaryResult(
                summary="Summary",
                key_points=["Point 1"],
                action_items=["Action 1"],
                tags=["billing"],
            ),
            quality_score=QualityScoreResult(
                tone_score=0.8,
                empathy_score=0.8,
                professionalism_score=0.9,
                resolution_score=0.75,
                overall_score=0.8,
                compliance_flags=[],
            ),
            routing=RoutingResult(
                route="standard_complete",
                used_fallback=False,
                reason="Quality checks passed",
            ),
        )


def test_analyze_call_transcript_input():
    fake_agent = FakeCallCenterAgent()
    app.dependency_overrides[get_call_center_agent] = lambda: fake_agent
    client = TestClient(app)

    response = client.post(
        "/api/v1/call-center/analyze",
        json={
            "session_id": "sess-transcript",
            "transcript": "Customer cannot access account and needs password reset.",
            "customer_id": "cust-1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "sess-transcript"
    assert body["transcript"] == "Customer cannot access account and needs password reset."
    assert body["intake"]["input_type"] == "transcript"

    app.dependency_overrides.clear()


def test_analyze_call_upload_audio_input():
    fake_agent = FakeCallCenterAgent()
    app.dependency_overrides[get_call_center_agent] = lambda: fake_agent
    client = TestClient(app)

    files = {"audio_file": ("sample.wav", b"fake-audio-bytes", "audio/wav")}
    data = {"session_id": "sess-audio", "customer_id": "cust-2"}

    response = client.post("/api/v1/call-center/analyze/upload", files=files, data=data)

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "sess-audio"
    assert body["intake"]["input_type"] == "audio"
    assert fake_agent.last_request is not None
    assert fake_agent.last_request.audio_base64 is not None
    assert fake_agent.last_request.audio_mime_type == "audio/wav"

    app.dependency_overrides.clear()


def test_analyze_call_upload_empty_file_returns_400():
    fake_agent = FakeCallCenterAgent()
    app.dependency_overrides[get_call_center_agent] = lambda: fake_agent
    client = TestClient(app)

    files = {"audio_file": ("empty.wav", b"", "audio/wav")}
    data = {"session_id": "sess-empty"}

    response = client.post("/api/v1/call-center/analyze/upload", files=files, data=data)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

    app.dependency_overrides.clear()
