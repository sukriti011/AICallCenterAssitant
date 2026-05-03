import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.agents.call_center.prompts import CALL_SUMMARIZATION_PROMPT
from app.agents.call_center.schemas import SummaryResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class SummarizationAgent:
    """Generates structured call summaries from transcript text."""

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=api_key,
        )

    async def run(self, transcript: str) -> SummaryResult:
        prompt = CALL_SUMMARIZATION_PROMPT.format(transcript=transcript)
        logger.info(
            f"[SummarizationAgent] START | transcript_word_count={len(transcript.split())}"
        )
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        parsed = self._parse(response.content)

        result = SummaryResult(
            summary=str(parsed.get("summary", "")).strip(),
            key_points=self._normalize_list(parsed.get("key_points", [])),
            action_items=self._normalize_list(parsed.get("action_items", [])),
            tags=self._normalize_list(parsed.get("tags", [])),
        )
        logger.info(
            f"[SummarizationAgent] END | key_points={len(result.key_points)} "
            f"action_items={len(result.action_items)} tags={result.tags}"
        )
        return result

    def _normalize_list(self, value: object) -> list[str]:
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
            logger.warning("Failed to parse summary JSON, using fallback")
            return {
                "summary": "Summary unavailable due to parsing issue.",
                "key_points": [],
                "action_items": [],
                "tags": ["fallback"],
            }
