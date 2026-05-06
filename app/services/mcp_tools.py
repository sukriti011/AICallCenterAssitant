"""
MCP-style local tool layer for call center analysis.

Each tool returns a dict with: name, status, details, timestamp, duration_ms.
Designed as a foundation to swap in real CRM / ticketing / refund APIs later.
"""

import time
from datetime import datetime, timezone

from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tool_result(name: str, status: str, details: str, start: float) -> dict:
    return {
        "name":        name,
        "status":      status,
        "details":     details,
        "timestamp":   _now_iso(),
        "duration_ms": round((time.perf_counter() - start) * 1000),
    }


# ── Individual tool functions ──────────────────────────────────────────────────

def get_customer_profile(customer_id: str) -> dict:
    name = "Customer Profile Checked"
    start = time.perf_counter()
    try:
        if not customer_id:
            return _tool_result(name, "Failed", "No customer_id provided", start)
        # Local stub — replace with real CRM lookup later
        details = f"Profile loaded for {customer_id}"
        logger.info(f"[MCPTools] get_customer_profile | customer_id={customer_id}")
        return _tool_result(name, "Success", details, start)
    except Exception as e:
        logger.error(f"[MCPTools] get_customer_profile error: {e}")
        return _tool_result(name, "Failed", str(e), start)


def check_refund_policy(transcript: str) -> dict:
    name = "Refund Policy Checked"
    start = time.perf_counter()
    try:
        keywords = ["refund", "billing", "charge", "payment", "invoice", "overcharged", "credit"]
        lower = transcript.lower()
        matched = [kw for kw in keywords if kw in lower]
        if matched:
            details = f"Refund-related keywords detected: {', '.join(matched)}"
        else:
            details = "No refund-related keywords detected"
        logger.info(f"[MCPTools] check_refund_policy | matched={matched}")
        return _tool_result(name, "Success", details, start)
    except Exception as e:
        logger.error(f"[MCPTools] check_refund_policy error: {e}")
        return _tool_result(name, "Failed", str(e), start)


def create_support_ticket(call_id: str, summary: str) -> dict:
    name = "Ticket Created"
    start = time.perf_counter()
    try:
        ticket_id = f"TKT-{call_id}-{int(time.time()) % 10000}"
        details = f"Support ticket {ticket_id} created for call {call_id}"
        logger.info(f"[MCPTools] create_support_ticket | call_id={call_id} ticket_id={ticket_id}")
        return _tool_result(name, "Success", details, start)
    except Exception as e:
        logger.error(f"[MCPTools] create_support_ticket error: {e}")
        return _tool_result(name, "Failed", str(e), start)


def notify_manager(call_id: str, reason: str) -> dict:
    name = "Manager Notified"
    start = time.perf_counter()
    try:
        details = f"Manager alert sent for call {call_id}: {reason}"
        logger.info(f"[MCPTools] notify_manager | call_id={call_id} reason={reason}")
        return _tool_result(name, "Success", details, start)
    except Exception as e:
        logger.error(f"[MCPTools] notify_manager error: {e}")
        return _tool_result(name, "Failed", str(e), start)


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_mcp_actions(
    call_id: str,
    customer_id: str,
    transcript: str,
    summary: str,
    escalation_needed: bool,
    risk_level: str,
) -> list[dict]:
    """
    Run MCP-style tool actions for a call analysis.

    Rules:
    - get_customer_profile: always
    - check_refund_policy: always
    - create_support_ticket: only if escalation_needed
    - notify_manager: only if escalation_needed or risk_level == "high"
    """
    actions: list[dict] = []

    # Always run
    actions.append(get_customer_profile(customer_id))
    actions.append(check_refund_policy(transcript))

    # Conditional
    if escalation_needed:
        actions.append(create_support_ticket(call_id, summary))
    else:
        actions.append({
            "name":        "Ticket Created",
            "status":      "Not Required",
            "details":     "Escalation not needed; no ticket created",
            "timestamp":   _now_iso(),
            "duration_ms": 0,
        })

    if escalation_needed or risk_level == "high":
        actions.append(notify_manager(call_id, f"risk_level={risk_level}, escalation={escalation_needed}"))
    else:
        actions.append({
            "name":        "Manager Notified",
            "status":      "Not Required",
            "details":     "Risk level normal; manager notification skipped",
            "timestamp":   _now_iso(),
            "duration_ms": 0,
        })

    logger.info(
        f"[MCPTools] run_mcp_actions complete | call_id={call_id} "
        f"escalation={escalation_needed} risk={risk_level} actions={len(actions)}"
    )
    return actions
