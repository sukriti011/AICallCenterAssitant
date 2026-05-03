import base64

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.agents.call_center.agent import CallCenterAgent, get_call_center_agent
from app.agents.call_center.schemas import (
    AnalyzeCallRequest,
    AnalyzeCallResponse,
    CallCenterRequest,
    CallCenterResponse,
    IntakeTranscribeResponse,
)
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/chat", response_model=CallCenterResponse)
async def chat(
    request: CallCenterRequest,
    agent: CallCenterAgent = Depends(get_call_center_agent),
):
    """Send a message to the Call Center Assistant and receive a response."""
    try:
        return await agent.chat(request)
    except Exception as e:
        logger.error(f"Call center chat error: {e}")
        raise HTTPException(status_code=500, detail="Agent error, please try again.")


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    agent: CallCenterAgent = Depends(get_call_center_agent),
):
    """Clear conversation history for a session."""
    cleared = agent.clear_session(session_id)
    return {"cleared": cleared, "session_id": session_id}


@router.post("/intake", response_model=IntakeTranscribeResponse)
async def intake_call(
    request: AnalyzeCallRequest,
    agent: CallCenterAgent = Depends(get_call_center_agent),
):
    """Run intake and transcription only — returns the parsed transcript without full analysis."""
    try:
        return await agent.intake_and_transcribe(request)
    except ValueError as e:
        logger.warning(f"Intake validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Intake error: {e}")
        raise HTTPException(status_code=500, detail="Intake error, please try again.")


@router.post("/intake/upload", response_model=IntakeTranscribeResponse)
async def intake_call_upload(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    customer_id: str | None = Form(None),
    agent: CallCenterAgent = Depends(get_call_center_agent),
):
    """Run intake and transcription from an uploaded audio file."""
    try:
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise ValueError("Uploaded audio_file is empty")

        request = AnalyzeCallRequest(
            session_id=session_id,
            customer_id=customer_id,
            audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
            audio_mime_type=audio_file.content_type or "audio/wav",
        )
        return await agent.intake_and_transcribe(request)
    except ValueError as e:
        logger.warning(f"Intake upload validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Intake upload error: {e}")
        raise HTTPException(status_code=500, detail="Intake upload error, please try again.")


@router.post("/analyze", response_model=AnalyzeCallResponse)
async def analyze_call(
    request: AnalyzeCallRequest,
    agent: CallCenterAgent = Depends(get_call_center_agent),
):
    """Run full call-insights pipeline through intake, transcription, summary, QA, and routing."""
    try:
        return await agent.analyze_call(request)
    except ValueError as e:
        logger.warning(f"Call analysis validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Call analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis error, please try again.")


@router.post("/analyze/upload", response_model=AnalyzeCallResponse)
async def analyze_call_upload(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    customer_id: str | None = Form(None),
    debug_force_fallback: bool = Form(False),
    agent: CallCenterAgent = Depends(get_call_center_agent),
):
    """Run full call-insights pipeline from uploaded audio."""
    try:
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise ValueError("Uploaded audio_file is empty")

        request = AnalyzeCallRequest(
            session_id=session_id,
            customer_id=customer_id,
            audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
            audio_mime_type=audio_file.content_type or "audio/wav",
            debug_force_fallback=debug_force_fallback,
        )
        return await agent.analyze_call(request)
    except ValueError as e:
        logger.warning(f"Call analysis upload validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Call analysis upload error: {e}")
        raise HTTPException(status_code=500, detail="Analysis error, please try again.")
