from app.agents.call_center.schemas import QualityScoreResult, RoutingResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class RoutingAgent:
    """Routes outcomes and marks fallback decisions from score quality."""

    async def run(self, quality_score: QualityScoreResult) -> RoutingResult:
        logger.info(
            f"[RoutingAgent] START | overall_score={quality_score.overall_score:.2f} "
            f"compliance_flags={quality_score.compliance_flags}"
        )
        if quality_score.overall_score < 0.4:
            result = RoutingResult(
                route="human_review",
                used_fallback=True,
                reason="Low overall QA score",
            )
            logger.info(f"[RoutingAgent] END | route={result.route} reason='{result.reason}'")
            return result

        if quality_score.compliance_flags:
            result = RoutingResult(
                route="compliance_review",
                used_fallback=False,
                reason="Compliance flags detected",
            )
            logger.info(f"[RoutingAgent] END | route={result.route} reason='{result.reason}'")
            return result

        result = RoutingResult(
            route="standard_complete",
            used_fallback=False,
            reason="Quality checks passed",
        )
        logger.info(f"[RoutingAgent] END | route={result.route} reason='{result.reason}'")
        return result
