import json
from time import perf_counter
from typing import Any, TypedDict

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.call_center.prompts import chat_prompt, INTENT_CLASSIFICATION_PROMPT
from app.agents.call_center.schemas import (
    AnalyzeCallRequest,
    AnalyzeCallResponse,
    CallCenterRequest,
    CallCenterResponse,
    Intent,
    IntakeResult,
    IntakeTranscribeResponse,
    PipelineTraceItem,
    QualityScoreResult,
    RoutingResult,
    SummaryResult,
    TranscriptionResult,
)
from app.agents.call_center.intake_agent import IntakeAgent
from app.agents.call_center.transcription_agent import TranscriptionAgent
from app.agents.call_center.summarization_agent import SummarizationAgent
from app.agents.call_center.quality_score_agent import QualityScoreAgent
from app.agents.call_center.routing_agent import RoutingAgent
from app.services.mcp_tools import run_mcp_actions
from app.core.config import get_settings
from app.core.logging import get_logger

try:
    from langgraph.graph import START, END, StateGraph
except ImportError:
    START = END = StateGraph = None

logger = get_logger(__name__)

# In-memory session store: session_id -> ConversationBufferWindowMemory
_session_store: dict[str, ConversationBufferWindowMemory] = {}


def _get_or_create_memory(session_id: str) -> ConversationBufferWindowMemory:
    if session_id not in _session_store:
        _session_store[session_id] = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history",
        )
        logger.info(f"Created new session: {session_id}")
    return _session_store[session_id]


def _parse_intent_response(raw: str) -> dict:
    """Safely parse the LLM JSON intent response."""
    try:
        # Strip markdown code fences if present
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        logger.warning(f"Failed to parse intent JSON: {raw}")
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "escalate": False,
            "suggested_actions": [],
        }


class CallCenterAgent:
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=settings.openai_api_key,
        )
        self.intent_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            api_key=settings.openai_api_key,
        )
        self.intake_agent = IntakeAgent()
        self.transcription_agent = TranscriptionAgent(api_key=settings.openai_api_key)
        self.summarization_agent = SummarizationAgent(api_key=settings.openai_api_key)
        self.quality_score_agent = QualityScoreAgent(api_key=settings.openai_api_key)
        self.routing_agent = RoutingAgent()
        self.analysis_graph = self._build_analysis_graph()

    def _build_analysis_graph(self):
        if StateGraph is None:
            logger.warning("LangGraph is not installed; using sequential analysis fallback")
            return None

        class AnalysisState(TypedDict):
            request: AnalyzeCallRequest
            intake: IntakeResult
            transcription: TranscriptionResult
            summary: SummaryResult
            quality_score: QualityScoreResult
            routing: RoutingResult
            intake_duration: str
            transcription_duration: str
            summarization_duration: str
            quality_scoring_duration: str
            routing_duration: str

        graph = StateGraph(AnalysisState)
        graph.add_node("intake_node", self._intake_node)
        graph.add_node("transcription_node", self._transcription_node)
        graph.add_node("summarization_node", self._summarization_node)
        graph.add_node("quality_scoring_node", self._quality_node)
        graph.add_node("routing_node", self._routing_node)

        graph.add_edge(START, "intake_node")
        graph.add_edge("intake_node", "transcription_node")
        graph.add_edge("transcription_node", "summarization_node")
        graph.add_edge("summarization_node", "quality_scoring_node")
        graph.add_edge("quality_scoring_node", "routing_node")
        graph.add_edge("routing_node", END)
        return graph.compile()

    async def _intake_node(self, state: dict[str, Any]) -> dict[str, Any]:
        logger.info("[Graph] intake_node -> running IntakeAgent")
        t0 = perf_counter()
        intake = await self.intake_agent.run(state["request"])
        duration = f"{perf_counter() - t0:.1f}s"
        logger.info(
            f"[Graph] intake_node -> done | input_type={intake.input_type.value} "
            f"word_count={intake.transcript_word_count} -> handoff to transcription_node"
        )
        return {"intake": intake, "intake_duration": duration}

    async def _transcription_node(self, state: dict[str, Any]) -> dict[str, Any]:
        logger.info("[Graph] transcription_node -> running TranscriptionAgent")
        t0 = perf_counter()
        transcription = await self.transcription_agent.run(state["request"])
        duration = f"{perf_counter() - t0:.1f}s"
        logger.info(
            f"[Graph] transcription_node -> done | source={transcription.source} "
            f"word_count={len(transcription.transcript.split())} -> handoff to summarization_node + quality_node"
        )
        return {"transcription": transcription, "transcription_duration": duration}

    async def _summarization_node(self, state: dict[str, Any]) -> dict[str, Any]:
        logger.info("[Graph] summarization_node -> running SummarizationAgent")
        t0 = perf_counter()
        summary = await self.summarization_agent.run(state["transcription"].transcript)
        duration = f"{perf_counter() - t0:.1f}s"
        logger.info(
            f"[Graph] summarization_node -> done | key_points={len(summary.key_points)} "
            f"action_items={len(summary.action_items)} -> handoff to quality_node"
        )
        return {"summary": summary, "summarization_duration": duration}

    async def _quality_node(self, state: dict[str, Any]) -> dict[str, Any]:
        logger.info("[Graph] quality_node -> running QualityScoreAgent")
        t0 = perf_counter()
        quality_score = await self.quality_score_agent.run(state["transcription"].transcript)
        duration = f"{perf_counter() - t0:.1f}s"
        logger.info(
            f"[Graph] quality_node -> done | overall_score={quality_score.overall_score:.2f} "
            f"compliance_flags={quality_score.compliance_flags} -> handoff to routing_node"
        )
        return {"quality_score": quality_score, "quality_scoring_duration": duration}

    async def _routing_node(self, state: dict[str, Any]) -> dict[str, Any]:
        logger.info("[Graph] routing_node -> running RoutingAgent")
        t0 = perf_counter()
        routing = await self.routing_agent.run(state["quality_score"])
        duration = f"{perf_counter() - t0:.1f}s"
        logger.info(
            f"[Graph] routing_node -> done | route={routing.route} "
            f"used_fallback={routing.used_fallback} reason='{routing.reason}' -> END"
        )
        return {"routing": routing, "routing_duration": duration}

    async def classify_intent(self, message: str) -> dict:
        prompt = INTENT_CLASSIFICATION_PROMPT.format(message=message)
        response = await self.intent_llm.ainvoke([HumanMessage(content=prompt)])
        return _parse_intent_response(response.content)

    async def chat(self, request: CallCenterRequest) -> CallCenterResponse:
        memory = _get_or_create_memory(request.session_id)

        # Classify intent in parallel with building the chat chain
        logger.info(
            f"[CallCenterAgent.chat] START | session={request.session_id} "
            f"history_turns={len(memory.chat_memory.messages) // 2}"
        )
        intent_data = await self.classify_intent(request.message)

        # Build messages from history + new input
        history = memory.chat_memory.messages
        messages = chat_prompt.format_messages(
            chat_history=history,
            input=request.message,
        )

        logger.info(
            f"[CallCenterAgent.chat] intent_classified | session={request.session_id} "
            f"intent={intent_data.get('intent')} confidence={intent_data.get('confidence')} "
            f"escalate={intent_data.get('escalate')} -> invoking LLM"
        )

        response = await self.llm.ainvoke(messages)
        reply = response.content

        # Persist turn to memory
        memory.chat_memory.add_user_message(request.message)
        memory.chat_memory.add_ai_message(reply)

        intent_str = intent_data.get("intent", "unknown")
        try:
            detected_intent = Intent(intent_str)
        except ValueError:
            detected_intent = Intent.UNKNOWN

        result = CallCenterResponse(
            session_id=request.session_id,
            response=reply,
            detected_intent=detected_intent,
            confidence=float(intent_data.get("confidence", 0.0)),
            suggested_actions=intent_data.get("suggested_actions", []),
            escalate=bool(intent_data.get("escalate", False)),
        )
        logger.info(
            f"[CallCenterAgent.chat] END | session={request.session_id} "
            f"detected_intent={result.detected_intent.value} escalate={result.escalate}"
        )
        return result

    async def analyze_call(self, request: AnalyzeCallRequest) -> AnalyzeCallResponse:
        logger.info(
            f"[CallCenterAgent.analyze_call] START | session={request.session_id} "
            f"customer_id={request.customer_id} "
            f"mode={'graph' if self.analysis_graph is not None else 'sequential'}"
        )

        pipeline_trace: list[PipelineTraceItem] = []

        if self.analysis_graph is not None:
            try:
                result = await self.analysis_graph.ainvoke({"request": request})
                intake = result["intake"]
                transcription = result["transcription"]
                summary = result["summary"]
                quality_score = result["quality_score"]
                routing = result["routing"]
                pipeline_trace = [
                    PipelineTraceItem(step="Intake Agent",        status="ok", detail="intake",         duration=result.get("intake_duration", "")),
                    PipelineTraceItem(step="Transcription Agent", status="ok", detail="transcription",  duration=result.get("transcription_duration", "")),
                    PipelineTraceItem(step="Summarization Agent", status="ok", detail="summarization",  duration=result.get("summarization_duration", "")),
                    PipelineTraceItem(step="QA Scoring Agent",    status="ok", detail="quality_scoring",duration=result.get("quality_scoring_duration", "")),
                    PipelineTraceItem(step="Routing Agent",       status="ok", detail="routing",        duration=result.get("routing_duration", "")),
                ]
                logger.info(
                    f"[CallCenterAgent.analyze_call] LangGraph pipeline complete | "
                    f"session={request.session_id} route={routing.route}"
                )
            except Exception as e:
                logger.warning(f"LangGraph analysis failed, using sequential fallback: {e}")
                pipeline_trace.append(
                    PipelineTraceItem(step="graph", status="fallback", detail=str(e), duration="n/a")
                )
                intake, transcription, summary, quality_score, routing, trace = await self._run_sequential_analysis(
                    request
                )
                pipeline_trace.extend(trace)
        else:
            intake, transcription, summary, quality_score, routing, trace = await self._run_sequential_analysis(
                request
            )
            pipeline_trace.extend(trace)

        if request.debug_force_fallback:
            routing = RoutingResult(
                route="human_review",
                used_fallback=True,
                reason="Demo override: forced fallback route",
            )
            pipeline_trace.append(
                PipelineTraceItem(step="routing", status="forced", detail="debug_force_fallback=true", duration="0.0s")
            )
            logger.info(f"[CallCenterAgent.analyze_call] debug_force_fallback applied | session={request.session_id}")

        response = AnalyzeCallResponse(
            session_id=request.session_id,
            transcript=transcription.transcript,
            intake=intake,
            summary=summary,
            quality_score=quality_score,
            routing=routing,
            pipeline_trace=pipeline_trace,
            mcp_actions=run_mcp_actions(
                call_id=request.session_id,
                customer_id=request.customer_id or "",
                transcript=transcription.transcript,
                summary=summary.summary,
                escalation_needed=routing.route == "human_review" or bool(quality_score.compliance_flags),
                risk_level="high" if quality_score.overall_score < 0.5 or bool(quality_score.compliance_flags) else "normal",
            ),
        )
        logger.info(
            f"[CallCenterAgent.analyze_call] END | session={request.session_id} "
            f"route={routing.route} overall_score={quality_score.overall_score:.2f} "
            f"pipeline_steps={len(pipeline_trace)}"
        )
        return response

    async def intake_and_transcribe(self, request: AnalyzeCallRequest) -> IntakeTranscribeResponse:
        """Run only the intake and transcription agents, returning the parsed transcript."""
        logger.info(f"[CallCenterAgent.intake_and_transcribe] START | session={request.session_id}")
        intake = await self.intake_agent.run(request)
        transcription = await self.transcription_agent.run(request)
        logger.info(
            f"[CallCenterAgent.intake_and_transcribe] END | session={request.session_id} "
            f"source={transcription.source} words={len(transcription.transcript.split())}"
        )
        return IntakeTranscribeResponse(
            session_id=request.session_id,
            transcript=transcription.transcript,
            source=transcription.source,
            intake=intake,
        )

    async def _run_sequential_analysis(self, request: AnalyzeCallRequest):
        trace: list[PipelineTraceItem] = []

        logger.info(f"[Sequential] START | session={request.session_id}")
        intake_started = perf_counter()
        intake = await self.intake_agent.run(request)
        trace.append(
            PipelineTraceItem(
                step="intake",
                status="ok",
                detail="sequential",
                duration=f"{perf_counter() - intake_started:.1f}s",
            )
        )
        logger.info(
            f"[Sequential] intake -> transcription | session={request.session_id} "
            f"input_type={intake.input_type.value}"
        )

        transcription_started = perf_counter()
        transcription = await self.transcription_agent.run(request)
        trace.append(
            PipelineTraceItem(
                step="transcription",
                status="ok",
                detail=transcription.source,
                duration=f"{perf_counter() - transcription_started:.1f}s",
            )
        )
        logger.info(
            f"[Sequential] transcription -> summarization + quality_scoring | "
            f"session={request.session_id} source={transcription.source} "
            f"word_count={len(transcription.transcript.split())}"
        )

        try:
            summarization_started = perf_counter()
            summary = await self.summarization_agent.run(transcription.transcript)
            trace.append(
                PipelineTraceItem(
                    step="summarization",
                    status="ok",
                    detail="sequential",
                    duration=f"{perf_counter() - summarization_started:.1f}s",
                )
            )
            logger.info(
                f"[Sequential] summarization -> quality_scoring | session={request.session_id} "
                f"key_points={len(summary.key_points)} action_items={len(summary.action_items)}"
            )
        except Exception as e:
            logger.warning(f"Summarization failed, using fallback: {e}")
            summary = SummaryResult(
                summary="Summary unavailable due to processing error.",
                key_points=[],
                action_items=[],
                tags=["fallback"],
            )
            trace.append(PipelineTraceItem(step="summarization", status="fallback", detail=str(e), duration="n/a"))

        try:
            quality_started = perf_counter()
            quality_score = await self.quality_score_agent.run(transcription.transcript)
            trace.append(
                PipelineTraceItem(
                    step="quality_scoring",
                    status="ok",
                    detail="sequential",
                    duration=f"{perf_counter() - quality_started:.1f}s",
                )
            )
        except Exception as e:
            logger.warning(f"Quality scoring failed, using fallback: {e}")
            quality_score = QualityScoreResult(
                tone_score=0.0,
                empathy_score=0.0,
                professionalism_score=0.0,
                resolution_score=0.0,
                overall_score=0.0,
                compliance_flags=["qa_runtime_fallback"],
            )
            trace.append(PipelineTraceItem(step="quality_scoring", status="fallback", detail=str(e), duration="n/a"))

        try:
            routing_started = perf_counter()
            routing = await self.routing_agent.run(quality_score)
            trace.append(
                PipelineTraceItem(
                    step="routing",
                    status="ok",
                    detail=routing.route,
                    duration=f"{perf_counter() - routing_started:.1f}s",
                )
            )
        except Exception as e:
            logger.warning(f"Routing failed, using fallback route: {e}")
            routing = RoutingResult(
                route="human_review",
                used_fallback=True,
                reason="Routing fallback due to processing error",
            )
            trace.append(PipelineTraceItem(step="routing", status="fallback", detail=str(e), duration="n/a"))

        return intake, transcription, summary, quality_score, routing, trace

    def clear_session(self, session_id: str) -> bool:
        if session_id in _session_store:
            del _session_store[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        return False


# Module-level singleton
_agent_instance: CallCenterAgent | None = None


def get_call_center_agent() -> CallCenterAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CallCenterAgent()
    return _agent_instance
