from app.agents.call_center.schemas import AnalyzeCallRequest, CallInputType, IntakeResult


class IntakeAgent:
    """Validates request payload and extracts simple intake metadata."""

    async def run(self, request: AnalyzeCallRequest) -> IntakeResult:
        has_transcript = bool(request.transcript and request.transcript.strip())
        has_audio = bool(request.audio_base64 and request.audio_base64.strip())
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info(
            f"[IntakeAgent] START | session={request.session_id} "
            f"has_transcript={has_transcript} has_audio={has_audio}"
        )

        if not has_transcript and not has_audio:
            raise ValueError("Either transcript or audio_base64 is required")

        input_type = CallInputType.TRANSCRIPT if has_transcript else CallInputType.AUDIO
        word_count = len(request.transcript.split()) if has_transcript and request.transcript else 0

        result = IntakeResult(
            session_id=request.session_id,
            customer_id=request.customer_id,
            input_type=input_type,
            has_audio=has_audio,
            transcript_word_count=word_count,
        )
        logger.info(
            f"[IntakeAgent] END | session={request.session_id} "
            f"input_type={input_type.value} word_count={word_count}"
        )
        return result
