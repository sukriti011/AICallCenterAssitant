import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.agents.call_center.guardrails import validate_compliance_flags
from app.agents.call_center.prompts import QUALITY_SCORING_PROMPT
from app.agents.call_center.schemas import QualityScoreResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class QualityScoreAgent:
    """Scores transcript quality using a fixed rubric output."""

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            api_key=api_key,
        )

    async def run(self, transcript: str) -> QualityScoreResult:
        prompt = QUALITY_SCORING_PROMPT.format(transcript=transcript)
        logger.info(
            f"[QualityScoreAgent] START | transcript_word_count={len(transcript.split())}"
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        parsed = self._parse(response.content)

        result = QualityScoreResult(
            tone_score=self._score(parsed.get("tone_score", 0.0)),
            empathy_score=self._score(parsed.get("empathy_score", 0.0)),
            professionalism_score=self._score(parsed.get("professionalism_score", 0.0)),
            resolution_score=self._score(parsed.get("resolution_score", 0.0)),
            compliance_flags=validate_compliance_flags(self._normalize_flags(parsed.get("compliance_flags", []))),
            overall_score=self._score(parsed.get("overall_score", 0.0)),
        )
        logger.info(
            f"[QualityScoreAgent] END | overall_score={result.overall_score:.2f} "
            f"tone={result.tone_score:.2f} empathy={result.empathy_score:.2f} "
            f"professionalism={result.professionalism_score:.2f} "
            f"resolution={result.resolution_score:.2f} "
            f"compliance_flags={result.compliance_flags}"
        )
        return result

    def _score(self, value: object) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))

    def _normalize_flags(self, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _parse(self, raw: str) -> dict:
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse QA JSON, using fallback")
            return {
                "tone_score": 0.0,
                "empathy_score": 0.0,
                "professionalism_score": 0.0,
                "resolution_score": 0.0,
                "overall_score": 0.0,
                "compliance_flags": ["qa_fallback"],
            }
