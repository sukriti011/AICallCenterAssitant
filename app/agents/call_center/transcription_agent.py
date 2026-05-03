import base64
import io
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from openai import AsyncOpenAI

from app.agents.call_center.guardrails import (
    detect_prompt_injection,
    redact_pii,
    validate_audio_size,
)
from app.agents.call_center.prompts import SPEAKER_DIARIZATION_PROMPT
from app.agents.call_center.schemas import AnalyzeCallRequest, TranscriptionResult
from app.core.logging import get_logger

logger = get_logger(__name__)

# Pattern to check if a transcript already has speaker labels
_SPEAKER_LABEL_RE = re.compile(r"(^|\n)\s*(Agent|Customer)\s*:", re.IGNORECASE)


class TranscriptionAgent:
    """Converts audio to transcript and normalizes transcript input."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            api_key=api_key,
        )

    async def run(self, request: AnalyzeCallRequest) -> TranscriptionResult:
        logger.info(f"[TranscriptionAgent] START | session={request.session_id}")
        if request.transcript and request.transcript.strip():
            raw = request.transcript.strip()
            transcript, pii_types = redact_pii(raw)
            injection = detect_prompt_injection(transcript)
            result = TranscriptionResult(
                transcript=transcript,
                source="provided_transcript",
                pii_redacted=bool(pii_types),
                pii_types_found=pii_types,
                injection_warning=injection,
            )
            logger.info(
                f"[TranscriptionAgent] END | session={request.session_id} "
                f"source=provided_transcript word_count={len(result.transcript.split())} "
                f"pii_redacted={result.pii_redacted} injection_warning={result.injection_warning}"
            )
            return result

        if not request.audio_base64:
            raise ValueError("audio_base64 is required when transcript is not provided")

        audio_bytes = base64.b64decode(request.audio_base64)
        validate_audio_size(audio_bytes, session_id=request.session_id)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "call_audio.wav"

        logger.info(f"[TranscriptionAgent] Calling Whisper API | session={request.session_id}")
        result = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )

        transcript = (result.text or "").strip()
        if not transcript:
            raise ValueError("Transcription did not return text")

        # If Whisper output has no speaker labels, use an LLM to add diarization
        if not _SPEAKER_LABEL_RE.search(transcript):
            logger.info(
                f"[TranscriptionAgent] No speaker labels detected, running diarization LLM "
                f"| session={request.session_id}"
            )
            transcript = await self._add_speaker_labels(transcript)

        transcript, pii_types = redact_pii(transcript)
        injection = detect_prompt_injection(transcript)

        t_result = TranscriptionResult(
            transcript=transcript,
            source="whisper",
            pii_redacted=bool(pii_types),
            pii_types_found=pii_types,
            injection_warning=injection,
        )
        logger.info(
            f"[TranscriptionAgent] END | session={request.session_id} "
            f"source=whisper word_count={len(transcript.split())} "
            f"pii_redacted={t_result.pii_redacted} injection_warning={t_result.injection_warning}"
        )
        return t_result

    async def _add_speaker_labels(self, transcript: str) -> str:
        """Use an LLM to add Agent/Customer speaker labels (and sentiment hints) to raw Whisper text."""
        prompt = SPEAKER_DIARIZATION_PROMPT.format(transcript=transcript)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        labeled = (response.content or "").strip()
        # Fall back to original if the LLM returns nothing usable
        return labeled if labeled else transcript

