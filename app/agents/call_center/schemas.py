from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Intent(str, Enum):
    BILLING = "billing"
    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_MANAGEMENT = "account_management"
    COMPLAINT = "complaint"
    GENERAL_INQUIRY = "general_inquiry"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"


class CallCenterRequest(BaseModel):
    session_id: str
    message: str
    customer_id: Optional[str] = None


class CallCenterResponse(BaseModel):
    session_id: str
    response: str
    detected_intent: Intent
    confidence: float
    suggested_actions: list[str] = Field(default_factory=list)
    escalate: bool = False


class CallInputType(str, Enum):
    TRANSCRIPT = "transcript"
    AUDIO = "audio"


class AnalyzeCallRequest(BaseModel):
    session_id: str
    transcript: Optional[str] = None
    audio_base64: Optional[str] = None
    audio_mime_type: str = "audio/wav"
    customer_id: Optional[str] = None
    debug_force_fallback: bool = False


class IntakeResult(BaseModel):
    session_id: str
    customer_id: Optional[str] = None
    input_type: CallInputType
    has_audio: bool
    transcript_word_count: int = 0


class TranscriptionResult(BaseModel):
    transcript: str
    source: str
    pii_redacted: bool = False
    pii_types_found: list[str] = Field(default_factory=list)
    injection_warning: bool = False


class SummaryResult(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class QualityScoreResult(BaseModel):
    tone_score: float = 0.0
    empathy_score: float = 0.0
    professionalism_score: float = 0.0
    resolution_score: float = 0.0
    compliance_flags: list[str] = Field(default_factory=list)
    overall_score: float = 0.0


class RoutingResult(BaseModel):
    route: str
    used_fallback: bool = False
    reason: str = ""


class PipelineTraceItem(BaseModel):
    step: str
    status: str
    detail: str = ""
    duration: str = ""


class AnalyzeCallResponse(BaseModel):
    session_id: str
    transcript: str
    intake: IntakeResult
    summary: SummaryResult
    quality_score: QualityScoreResult
    routing: RoutingResult
    pipeline_trace: list[PipelineTraceItem] = Field(default_factory=list)
    mcp_actions: list[dict] = Field(default_factory=list)


class IntakeTranscribeResponse(BaseModel):
    session_id: str
    transcript: str
    source: str
    intake: IntakeResult
