from __future__ import annotations

import base64
import json
import os
import re
from html import escape
from typing import Any

import httpx
import streamlit as st

from mock_data import DEMO_RESULT, SAMPLE_TRANSCRIPTS, _MOCK_CALL_ANALYSIS, get_mock_call_records


_ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "CallCenterIcon_v1.jpg")
try:
    with open(_ICON_PATH, "rb") as _f:
        _ICON_B64 = base64.b64encode(_f.read()).decode("utf-8")
except FileNotFoundError:
    _ICON_B64 = ""


def _icon(name: str, size: int = 18) -> str:
    """Small inline icon set used by the Streamlit HTML UI."""
    icons = {
        "dashboard": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
        "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.4 2.1L8.1 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.6 1.9Z"/>',
        "analytics": '<path d="M4 19V9"/><path d="M10 19V5"/><path d="M16 19v-8"/><path d="M22 19V3"/>',
        "doc": '<path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7Z"/><path d="M14 2v5h5"/><path d="M9 13h6"/><path d="M9 17h6"/>',
        "user": '<path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="7" r="4"/>',
        "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M3 10h18"/>',
        "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
        "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>',
        "filter": '<path d="M22 3H2l8 9.5V20l4 2v-9.5Z"/>',
        "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
        "star": '<path d="m12 2 3 6.2 6.8 1-4.9 4.8 1.2 6.8-6.1-3.2-6.1 3.2 1.2-6.8-4.9-4.8 6.8-1Z"/>',
        "trend": '<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
        "sad": '<circle cx="12" cy="12" r="10"/><path d="M8 15s1.5-2 4-2 4 2 4 2"/><path d="M9 9h.01"/><path d="M15 9h.01"/>',
        "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
        "tag": '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/><path d="M7.5 7.5h.01"/>',
        "check": '<path d="M20 6 9 17l-5-5"/>',
        "bot": '<rect x="5" y="7" width="14" height="12" rx="2"/><path d="M12 7V3"/><path d="M8 11h.01"/><path d="M16 11h.01"/><path d="M9 16h6"/>',
    }
    body = icons.get(name, icons["doc"])
    return (
        f'<svg class="ui-icon" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def _render_app_sidebar(active: str) -> None:
    icon_html = (
        f'<img src="data:image/jpeg;base64,{_ICON_B64}" class="side-logo-img">'
        if _ICON_B64 else '<div class="side-logo-fallback"></div>'
    )

    # ── Brand (HTML only) ────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"""
        <div class="side-brand">
            {icon_html}
            <div class="side-brand-text">AI Call Center<br><span>Assistant</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Nav items as real Streamlit buttons ──────────────────────────────────
    items = [
        ("dashboard", "Dashboard"),
        ("records", "Call Records"),
        ("details", "Call Details"),
        ("analytics", "Analytics"),
    ]

    _screen_map = {
        "dashboard": "dashboard",
        "records": "dashboard",      # records list lives on the dashboard for now
        "details": "details",
        "analytics": "dashboard",    # analytics TBD
    }

    for key, label in items:
        is_active = key == active
        # Marker div — zero-height, used only for CSS active-state targeting
        marker_cls = "sidenav-active-marker" if is_active else "sidenav-marker"
        st.sidebar.markdown(f'<div class="{marker_cls}"></div>', unsafe_allow_html=True)
        if st.sidebar.button(label, key=f"sidenav_{key}", use_container_width=True):
            target = _screen_map[key]
            if target == "details" and not st.session_state.get("selected_call_id"):
                target = "dashboard"
            st.session_state["current_screen"] = target
            st.rerun()

    # ── Back to Dashboard (only on sub-screens) ──────────────────────────────
    if active != "dashboard":
        st.sidebar.markdown('<div class="sidenav-back-spacer"></div>', unsafe_allow_html=True)
        if st.sidebar.button("← Back to Dashboard", key="sidenav_back", use_container_width=True):
            st.session_state["current_screen"] = "dashboard"
            st.rerun()

    # ── Footer + profile (HTML only) ─────────────────────────────────────────
    st.sidebar.markdown(
        """
        <div class="side-footer">© 2026 AI Call Center Assistant<br>All rights reserved.</div>
        <div class="side-profile">
            <div class="side-avatar">TM</div>
            <div>
                <div class="side-profile-name">Team Lead</div>
                <div class="side-profile-role">Manager</div>
            </div>
            <div class="side-profile-spacer"></div>
            <span class="side-bell">⌄</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_dashboard_date(raw: str) -> tuple[str, str]:
    date_part, time_part = raw.split(" ", 1)
    yyyy, mm, dd = date_part.split("-")
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
    }
    hour, minute = time_part.split(":")
    hour_i = int(hour)
    suffix = "AM" if hour_i < 12 else "PM"
    hour_12 = hour_i % 12 or 12
    return f"{months[mm]} {int(dd)}, {yyyy}", f"{hour_12}:{minute} {suffix}"


def load_selected_call(call_id: str) -> None:
    """Populate session state with the analysis result for the given call_id.

    Looks up the per-call analysis from _MOCK_CALL_ANALYSIS.
    Falls back to DEMO_RESULT for any unknown call_id.
    Replace _MOCK_CALL_ANALYSIS with a real DB / API lookup to go live.
    """
    result = _MOCK_CALL_ANALYSIS.get(call_id, DEMO_RESULT)

    st.session_state["analysis_result"] = result
    st.session_state["transcript_input"] = result.get("transcript", "")
    st.session_state["parsed_transcript"] = result.get("transcript", "")
    st.session_state["parsed_source"] = "labeled"
    st.session_state["kp_escalation"] = result.get("routing", {}).get("used_fallback", False)
    st.session_state["kp_sentiment"] = _infer_sentiment(result)

def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def _post_upload(
    url: str,
    session_id: str,
    customer_id: str,
    audio_bytes: bytes,
    file_name: str,
    mime_type: str,
    debug_force_fallback: bool,
) -> dict[str, Any]:
    with httpx.Client(timeout=120.0) as client:
        files = {"audio_file": (file_name, audio_bytes, mime_type or "audio/wav")}
        data = {"session_id": session_id}
        if customer_id:
            data["customer_id"] = customer_id
        data["debug_force_fallback"] = str(debug_force_fallback).lower()
        response = client.post(url, files=files, data=data)
    response.raise_for_status()
    return response.json()


def _highlight_keywords(text: str) -> str:
    escaped = escape(text)
    for word in ["refund", "verify", "escalation", "billing", "compliance"]:
        pattern = re.compile(rf"({word})", re.IGNORECASE)
        escaped = pattern.sub(r"<span class='hl'>\1</span>", escaped)
    return escaped


def _to_transcript_rows(transcript: str) -> list[dict[str, str]]:
    if not transcript.strip():
        return []

    # Normalize: replace newlines before known speaker labels so the regex works
    # whether the transcript uses newlines or inline "Agent: ... Customer: ..." layout
    normalized = re.sub(r"\n+([Aa]gent|[Cc]ustomer):", r" \1:", transcript)
    pattern = r"(Agent|Customer):\s*(.*?)(?=(?:Agent|Customer):|$)"
    matches = re.findall(pattern, normalized, flags=re.IGNORECASE | re.DOTALL)

    rows: list[dict[str, str]] = []
    sec = 1
    # Extract optional sentiment marker at start of utterance: e.g. [annoyed], [apologetic]
    _sentiment_re = re.compile(r"^\[([^\]]+)\]\s*", re.IGNORECASE)

    for speaker, text in matches[:20]:
        clean_text = " ".join(text.split())
        if not clean_text:
            continue
        sentiment = ""
        m = _sentiment_re.match(clean_text)
        if m:
            sentiment = m.group(1)
            clean_text = clean_text[m.end():]
        rows.append(
            {
                "speaker": speaker.capitalize(),
                "text": clean_text,
                "sentiment": sentiment,
                "time": f"00:{sec:02d}",
            }
        )
        sec += 4

    return rows


def _build_conversation_html(rows: list[dict[str, str]], show_timestamps: bool = False) -> str:
    """Render transcript rows as a chat-style conversation.

    Speaker labels are bold blue. Sentiment markers (e.g. [annoyed]) are shown
    only when present in the row (i.e. when detected from audio); sample text
    without sentiment markers will simply omit them.
    """
    parts: list[str] = []
    for row in rows:
        speaker_html = (
            f'<strong style="color:#2563EB;font-size:0.9rem">'
            f'{escape(row["speaker"])}:</strong>'
        )
        sentiment = row.get("sentiment", "")
        sentiment_html = (
            f' <span style="color:#6b7280;font-style:italic;font-size:0.88rem">'
            f'[{escape(sentiment)}]</span>'
        ) if sentiment else ""
        time_html = (
            f'<span style="color:#9ca3af;font-size:0.82rem;margin-left:auto;flex-shrink:0">'
            f'{escape(row["time"])}</span>'
        ) if show_timestamps else ""
        text_html = _highlight_keywords(row["text"])
        parts.append(
            f'<div style="padding:0.6rem 0.9rem;border-bottom:1px solid #E2E8F0;">'
            f'<div style="display:flex;align-items:center;gap:0.2rem;margin-bottom:0.22rem;'
            f'flex-wrap:wrap">'
            f'{speaker_html}{sentiment_html}{time_html}'
            f'</div>'
            f'<div style="color:#0F172A;font-size:0.9rem;line-height:1.5">{text_html}</div>'
            f'</div>'
        )
    return "".join(parts)


def _infer_sentiment(result: dict[str, Any]) -> str:
    """Infer overall customer sentiment from transcript markers.

    Returns 'Frustrated', 'Happy', or 'Neutral'.
    """
    transcript = result.get("transcript", "")
    rows = _to_transcript_rows(transcript)
    frustrated_words = {"frustrated", "annoyed", "angry", "upset", "unhappy", "furious", "irritated", "disappointed"}
    happy_words = {"happy", "satisfied", "pleased", "delighted", "grateful", "thankful"}
    for row in rows:
        if row["speaker"].lower() == "customer" and row.get("sentiment"):
            s = row["sentiment"].lower()
            if any(w in s for w in frustrated_words):
                return "Frustrated"
            if any(w in s for w in happy_words):
                return "Happy"
    return "Neutral"


def _render_header() -> None:
    icon_html = (
        f'<img src="data:image/jpeg;base64,{_ICON_B64}" '
        'style="width:52px;height:52px;border-radius:12px;object-fit:cover;flex-shrink:0;">'
    ) if _ICON_B64 else '<div class="orb"></div>'
    st.markdown(
        f"""
        <div class="top-shell">
            <div class="top-title-wrap">
                {icon_html}
                <div>
                    <h1 class="title">AI Call Center Assistant</h1>
                    <div class="subtitle">Upload a call recording or transcript to generate summary, QA score, and action items.</div>
                </div>
            </div>
            <div class="top-actions"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_transcript_panel(result: dict[str, Any], search_text: str, show_timestamps: bool) -> None:
    transcript = result.get("transcript", "")
    rows = _to_transcript_rows(transcript)

    if search_text:
        token = search_text.lower().strip()
        rows = [r for r in rows if token in r["text"].lower() or token in r["speaker"].lower()]

    if not rows:
        st.markdown('<div class="panel"><div class="muted">No transcript rows available.</div></div>', unsafe_allow_html=True)
        return

    st.markdown(
        f'<div class="transcript-box">{_build_conversation_html(rows, show_timestamps)}</div>',
        unsafe_allow_html=True,
    )


def _score_row(label: str, value: float) -> str:
    pct = max(0, min(100, int(round(value * 100))))
    return (
        f'<div class="progress-row">'
        f'<div class="progress-head"><span>{escape(label)}</span><span>{pct}%</span></div>'
        f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>'
        f'</div>'
    )


def _render_summary_column(result: dict[str, Any]) -> None:
    summary = result.get("summary", {})
    quality = result.get("quality_score", {})
    routing = result.get("routing", {})

    st.markdown(
        f"""
        <div class="mini-card">
            <p class="mini-title">Summary</p>
            <div class="hr"></div>
            <div class="muted">{escape(summary.get('summary', 'No summary generated.'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    key_points = summary.get("key_points", [])
    key_rows = "".join(f"<div class='meta-row'><span>{escape(point)}</span></div>" for point in key_points)
    st.markdown(
        f"""
        <div class="mini-card">
            <p class="mini-title">Key Points</p>
            <div class="hr"></div>
            {key_rows or "<div class='muted'>No key points found.</div>"}
            <div class="hr"></div>
            <div class="meta-row"><span>Escalation needed:</span><span>{str(routing.get('used_fallback', False))}</span></div>
            <div class="meta-row"><span>Sentiment:</span><span>Neutral</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_summary_card(result: dict[str, Any]) -> None:
    summary = result.get("summary", {})
    text = summary.get("summary", "No summary generated.")
    st.markdown(
        f"""
        <div class="mini-card">
            <p class="mini-title">Summary</p>
            <div class="hr"></div>
            <div class="muted">{escape(text[:220] + ('...' if len(text) > 220 else ''))}</div>
            <div class="hr"></div>
            <div class="soft-note">This excerpt mirrors the concise overview style from your reference.</div>
            <div style="display:flex;justify-content:flex-end"><span class="view-more">View More</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _summary_card_html(result: dict[str, Any]) -> str:
    summary = result.get("summary", {})
    text = summary.get("summary", "No summary generated.")
    b64 = base64.b64encode(text.encode("utf-8")).decode("utf-8")

    return f"""
        <div class="mini-card">
            <p class="mini-title">Summary</p>
            <div class="hr"></div>
            <div class="muted" style="line-height:1.6;max-height:160px;overflow-y:auto;padding-right:4px;">{escape(text)}</div>
            <div style="display:flex;justify-content:flex-end;margin-top:0.8rem;">
                <a href="data:text/plain;base64,{b64}" download="summary.txt" class="view-more" style="text-decoration:none;">Export Summary</a>
            </div>
        </div>
    """


def _render_key_points_card(result: dict[str, Any]) -> None:
    summary = result.get("summary", {})
    routing = result.get("routing", {})
    points = summary.get("key_points", [])
    customer_issue = points[0] if len(points) > 0 else "Customer issue: Not detected"
    resolution = points[1] if len(points) > 1 else "Resolution: Pending review"
    next_step = points[2] if len(points) > 2 else "Next Step: Follow-up required"
    sentiment = _infer_sentiment(result)
    st.markdown(
        f"""
        <div class="mini-card">
            <p class="mini-title">Key Points</p>
            <div class="hr"></div>
            <div class="meta-row"><span>{escape(customer_issue)}</span></div>
            <div class="meta-row"><span>{escape(resolution)}</span></div>
            <div class="meta-row"><span>{escape(next_step)}</span></div>
            <div class="hr"></div>
            <div class="meta-row"><span>Escalation needed:</span><span>{str(routing.get('used_fallback', False))}</span></div>
            <div class="meta-row"><span>Sentiment:</span><span>{sentiment}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _key_points_card_html(result: dict[str, Any]) -> str:
    summary = result.get("summary", {})
    routing = result.get("routing", {})
    points = summary.get("key_points", [])

    customer_issue = points[0].replace("Customer issue: ", "") if len(points) > 0 else "Not detected"
    resolution = points[1].replace("Resolution: ", "") if len(points) > 1 else "Pending review"
    next_step = points[2].replace("Next step: ", "").replace("Next Step: ", "") if len(points) > 2 else "Follow-up required"
    escalation = "Yes" if routing.get("used_fallback", False) else "No"
    sentiment = _infer_sentiment(result)

    return f"""
        <div class="mini-card">
            <p class="mini-title">Key Points</p>
            <div class="hr"></div>
            <div class="meta-row"><span>Customer issue:</span><span>{escape(customer_issue)}</span></div>
            <div class="meta-row"><span>Resolution:</span><span>{escape(resolution)}</span></div>
            <div class="meta-row"><span>Next step:</span><span>{escape(next_step)}</span></div>
            <div class="hr"></div>
            <div class="meta-row"><span>Escalation needed:</span><span>{escalation}</span></div>
            <div class="meta-row"><span>Sentiment:</span><span>{sentiment}</span></div>
        </div>
    """


def _render_key_points_card_interactive(result: dict[str, Any]) -> None:
    """Render the Key Points card with an interactive escalation toggle and sentiment selector."""
    summary = result.get("summary", {})
    points = summary.get("key_points", [])
    customer_issue = points[0].replace("Customer issue: ", "") if len(points) > 0 else "Not detected"
    resolution = points[1].replace("Resolution: ", "") if len(points) > 1 else "Pending review"
    next_step = (
        points[2].replace("Next step: ", "").replace("Next Step: ", "")
        if len(points) > 2
        else "Follow-up required"
    )

    with st.container(border=True):
        st.markdown(
            f"""
            <p class="mini-title" style="margin:0 0 0.45rem">Key Points</p>
            <div class="hr"></div>
            <div class="meta-row"><span>Customer issue:</span><span>{escape(customer_issue)}</span></div>
            <div class="meta-row"><span>Resolution:</span><span>{escape(resolution)}</span></div>
            <div class="meta-row"><span>Next step:</span><span>{escape(next_step)}</span></div>
            <div class="hr" style="margin-top:0.5rem;margin-bottom:0.1rem"></div>
            """,
            unsafe_allow_html=True,
        )
        sentiment = _infer_sentiment(result)
        escalation = result.get("routing", {}).get("used_fallback", False)
        options = ["Neutral", "Happy", "Frustrated"]
        if "kp_sentiment" not in st.session_state:
            st.session_state["kp_sentiment"] = sentiment
        if "kp_escalation" not in st.session_state:
            st.session_state["kp_escalation"] = escalation
        st.toggle("Escalation needed", key="kp_escalation")
        st.selectbox("Sentiment", options, key="kp_sentiment")


def _render_qa_card(result: dict[str, Any]) -> None:
    quality = result.get("quality_score", {})
    overall = int(round(float(quality.get("overall_score", 0.0)) * 100))
    bars = "".join(
        [
            _score_row("Tone", float(quality.get("tone_score", 0.0))),
            _score_row("Empathy", float(quality.get("empathy_score", 0.0))),
            _score_row("Professionalism", float(quality.get("professionalism_score", 0.0))),
            _score_row("Resolution Clarity", float(quality.get("resolution_score", 0.0))),
            _score_row("Compliance", 1.0 if not quality.get("compliance_flags", []) else 0.6),
        ]
    )
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="meta-row"><p class="mini-title" style="margin:0">QA Score</p><p class="mini-title" style="margin:0">{overall}/100</p></div>
            <div class="hr"></div>
            {bars}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _qa_card_html(result: dict[str, Any]) -> str:
    quality = result.get("quality_score", {})
    overall = int(round(float(quality.get("overall_score", 0.0)) * 100))
    bars = "".join(
        [
            _score_row("Tone", float(quality.get("tone_score", 0.0))),
            _score_row("Empathy", float(quality.get("empathy_score", 0.0))),
            _score_row("Professionalism", float(quality.get("professionalism_score", 0.0))),
            _score_row("Resolution Clarity", float(quality.get("resolution_score", 0.0))),
            _score_row("Compliance", 1.0 if not quality.get("compliance_flags", []) else 0.6),
        ]
    )
    return f"""
        <div class="mini-card">
            <div class="meta-row"><p class="mini-title" style="margin:0">QA Score</p><p class="score-big" style="margin:0">{overall}/100</p></div>
            <div class="hr"></div>
            {bars}
        </div>
    """


def _render_actions_card(result: dict[str, Any]) -> None:
    summary = result.get("summary", {})
    action_items = summary.get("action_items", [])
    action_rows = "".join(f"<li>{escape(item)}</li>" for item in action_items[:3])
    tags = summary.get("tags", [])
    tag_rows = []
    for index, tag in enumerate(tags[:5]):
        tag_class = "badge"
        if index in {3, 4}:
            tag_class = "badge badge-warm"
        elif index == 2:
            tag_class = "badge badge-neutral"
        tag_rows.append(f"<span class='{tag_class}'>{escape(tag)}</span>")
    st.markdown(
        f"""
        <div class="mini-card">
            <p class="mini-title">Action Items</p>
            <div class="hr"></div>
            <ul class="bullet-list">{action_rows or '<li>No action items generated.</li>'}</ul>
            <div class="hr"></div>
            {''.join(tag_rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _actions_card_html(result: dict[str, Any]) -> str:
    summary = result.get("summary", {})
    action_items = summary.get("action_items", [])
    action_rows = "".join(f"<li>{escape(item)}</li>" for item in action_items[:3])
    tags = summary.get("tags", [])
    tag_rows = []
    for index, tag in enumerate(tags[:5]):
        tag_class = "badge"
        if index in {3, 4}:
            tag_class = "badge badge-warm"
        elif index == 2:
            tag_class = "badge badge-neutral"
        tag_rows.append(f"<span class='{tag_class}'>{escape(tag)}</span>")
    return f"""
        <div class="mini-card">
            <p class="mini-title">Action Items</p>
            <div class="hr"></div>
            <ul class="bullet-list">{action_rows or '<li>No action items generated.</li>'}</ul>
            <div class="hr"></div>
            {''.join(tag_rows)}
        </div>
    """


def _detail_chip(icon_name: str, label: str, value: str) -> str:
    return (
        f'<span class="detail-chip">{_icon(icon_name, 17)}'
        f'<strong>{escape(label)}:</strong><span>{escape(value)}</span></span>'
    )


def _call_audio_card(duration: str) -> str:
    return f"""
        <div class="audio-card">
            <div class="card-title">Call Audio</div>
            <div class="audio-row">
                <button class="play-button">▶</button>
                <strong>00:00 / {escape(duration.replace("m ", ":").replace("s", "").zfill(5))}</strong>
                <div class="waveform">
                    <span></span><span></span><span></span><span></span><span></span><span></span>
                    <span></span><span></span><span></span><span></span><span></span><span></span>
                    <span class="wave-muted"></span><span class="wave-muted"></span><span class="wave-muted"></span>
                    <span class="wave-muted"></span><span class="wave-muted"></span><span class="wave-muted"></span>
                </div>
                <span class="audio-icon">⌕</span>
                <span class="audio-icon">⇩</span>
            </div>
        </div>
    """


def _transcript_table_html(rows: list[dict[str, str]]) -> str:
    parts = []
    for row in rows[:14]:
        speaker = row["speaker"]
        badge = "speaker-agent" if speaker == "Agent" else "speaker-customer"
        parts.append(
            f"""
            <div class="transcript-line">
                <span class="transcript-time">{escape(row["time"])}</span>
                <span class="speaker-pill {badge}">{_icon('user', 14)} {escape(speaker)}</span>
                <span class="transcript-copy">{escape(row["text"])}</span>
            </div>
            """
        )
    return "".join(parts)


def _score_color(value: float) -> str:
    pct = int(round(value * 100))
    if pct >= 80:
        return "#16A34A"
    if pct >= 70:
        return "#F97316"
    return "#EF4444"


def _qa_detail_html(result: dict[str, Any]) -> str:
    quality = result.get("quality_score", {})
    overall = int(round(float(quality.get("overall_score", 0.0)) * 100))
    rows = [
        ("Tone", float(quality.get("tone_score", 0.0))),
        ("Empathy", float(quality.get("empathy_score", 0.0))),
        ("Professionalism", float(quality.get("professionalism_score", 0.0))),
        ("Resolution Clarity", float(quality.get("resolution_score", 0.0))),
        ("Compliance", 1.0 if not quality.get("compliance_flags", []) else 0.81),
    ]
    bars = []
    for label, value in rows:
        pct = int(round(value * 100))
        bars.append(
            f'<div class="qa-line">'
            f'<div><span>{escape(label)}</span><strong>{pct}%</strong></div>'
            f'<div class="qa-track"><div style="width:{pct}%;background:{_score_color(value)}"></div></div>'
            f'</div>'
        )
    return (
        f'<div class="ref-card qa-ref-card">'
        f'<div class="ref-card-head">{_icon("shield", 20)}<strong>QA Score</strong>'
        f'<span class="qa-overall">{overall}%</span><span>Good</span></div>'
        f'{"".join(bars)}</div>'
    )


def _render_workflow(result: dict[str, Any]) -> None:
    trace = result.get("pipeline_trace", [])
    if not trace:
        trace = DEMO_RESULT["pipeline_trace"]

    fallback_times = {
        "intake agent": "1.2s", "transcription agent": "3.5s",
        "summarization agent": "2.8s", "qa scoring agent": "1.1s", "routing agent": "0.4s",
    }

    steps: list[dict] = []
    total_secs = 0.0
    for item in trace:
        step = item.get("step", "Agent")
        raw_dur = item.get("detail", "") or item.get("duration", "")
        duration = raw_dur or fallback_times.get(step.lower(), "—")
        status = item.get("status", "ok")
        try:
            total_secs += float(str(duration).rstrip("s"))
        except ValueError:
            pass
        steps.append({"label": step, "duration": str(duration), "status": status})

    step_parts: list[str] = []
    for i, s in enumerate(steps):
        chk_color = "#059669" if s["status"] == "ok" else "#D97706"
        chk_icon = "&#10003;" if s["status"] == "ok" else "&#9888;"
        arrow = "" if i == len(steps) - 1 else '<div class="wf-arrow" style="margin-top:1.6rem">&#8594;</div>'
        step_parts.append(
            f'<div style="display:flex;align-items:center;gap:0">'
            f'<div style="display:flex;flex-direction:column;align-items:center">'
            f'<div style="color:{chk_color};font-size:0.82rem;font-weight:700;margin-bottom:0.18rem">{chk_icon}</div>'
            f'<div class="wf-box"><div class="wf-box-label">{escape(s["label"])}</div>'
            f'<div class="wf-box-time">{escape(s["duration"])}</div></div>'
            f'</div>{arrow}</div>'
        )

    total_str = f"{total_secs:.1f}s"
    total_part = (
        f'<div style="display:flex;align-items:center;gap:0">'
        f'<div class="wf-arrow" style="margin-top:1.6rem">&#8594;</div>'
        f'<div style="display:flex;flex-direction:column;align-items:center">'
        f'<div style="color:#2563EB;font-size:0.82rem;font-weight:700;margin-bottom:0.18rem">&#9203;</div>'
        f'<div class="wf-box wf-box-total"><div class="wf-box-label" style="color:#2563EB">Total Time</div>'
        f'<div class="wf-box-time" style="color:#2563EB;font-weight:700">{total_str}</div></div>'
        f'</div></div>'
    )

    st.markdown(
        f"""
        <div class="wf-trace-card">
            <div class="wf-trace-head">
                <span class="wf-icon">&#129302;</span>
                <span class="wf-trace-title">Agent Workflow Trace</span>
            </div>
            <div class="wf-trace-steps">{''.join(step_parts)}{total_part}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _run_intake(
    api_url: str,
    session_id: str,
    customer_id: str,
    transcript: str | None,
    audio_file: Any,
) -> dict[str, Any]:
    """Call /intake or /intake/upload and return the parsed transcript response."""
    if audio_file is not None:
        try:
            audio_file.seek(0)
            audio_bytes = audio_file.read()
        except Exception:
            audio_bytes = audio_file.getvalue()
        if not audio_bytes:
            raise ValueError("Uploaded audio file is empty.")
        with httpx.Client(timeout=120.0) as client:
            files = {"audio_file": (audio_file.name, audio_bytes, audio_file.type or "audio/wav")}
            data = {"session_id": session_id}
            if customer_id:
                data["customer_id"] = customer_id
            response = client.post(f"{api_url}/intake/upload", files=files, data=data)
        response.raise_for_status()
        return response.json()

    if not transcript or not transcript.strip():
        raise ValueError("No transcript or audio to parse.")
    return _post_json(
        f"{api_url}/intake",
        {"session_id": session_id, "customer_id": customer_id or None, "transcript": transcript},
    )


def _run_analysis(
    api_url: str,
    session_id: str,
    customer_id: str,
    transcript: str,
    audio_file: Any,
    debug_force_fallback: bool,
) -> dict[str, Any]:
    if audio_file is not None:
        # UploadedFile behaves like a stream; reset/read safely across reruns.
        try:
            audio_file.seek(0)
            audio_bytes = audio_file.read()
        except Exception:
            audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            raise ValueError("Uploaded audio file is empty. Please upload a valid file and try again.")

        return _post_upload(
            f"{api_url}/analyze/upload",
            session_id=session_id,
            customer_id=customer_id,
            audio_bytes=audio_bytes,
            file_name=audio_file.name,
            mime_type=audio_file.type or "audio/wav",
            debug_force_fallback=debug_force_fallback,
        )

    if not transcript.strip():
        raise ValueError("Transcript is required when no audio file is uploaded.")

    return _post_json(
        f"{api_url}/analyze",
        {
            "session_id": session_id,
            "customer_id": customer_id or None,
            "transcript": transcript,
            "debug_force_fallback": debug_force_fallback,
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sentiment_badge(sentiment: str) -> str:
    mapping = {
        "Happy": "badge-green",
        "Frustrated": "badge-red",
        "Neutral": "badge-yellow",
    }
    cls = mapping.get(sentiment, "badge-neutral")
    label = {"Happy": "Positive", "Frustrated": "Negative"}.get(sentiment, sentiment)
    face = {"Happy": "☺", "Frustrated": "☹", "Neutral": "⊙"}.get(sentiment, "⊙")
    return f'<span class="{cls}">{face}&nbsp;{escape(label)}</span>'


def _risk_badge(risk: str) -> str:
    mapping = {"Low": "badge-green", "Medium": "badge-yellow", "High": "badge-red"}
    cls = mapping.get(risk, "badge-neutral")
    return f'<span class="{cls}">{escape(risk)}</span>'


def _status_badge(status: str) -> str:
    mapping = {"Completed": "badge-green", "Escalated": "badge-red", "In Progress": "badge-yellow"}
    cls = mapping.get(status, "badge-neutral")
    return f'<span class="{cls}">{escape(status)}</span>'


def _bool_indicator(value: bool, true_label: str = "Yes", false_label: str = "No") -> str:
    """Render a green check or red cross indicator with a label."""
    if value:
        return (
            f'<span style="color:#059669;font-weight:600">'  
            f'<span style="font-size:0.95rem">&#10003;</span> {escape(true_label)}</span>'
        )
    return (
        f'<span style="color:#94A3B8;font-weight:500">'  
        f'<span style="font-size:0.95rem">&#8722;</span> {escape(false_label)}</span>'
    )


def _risk_level_html(level: str) -> str:
    """Inline colored risk level label."""
    colors = {"Low": ("#ECFDF5", "#059669"), "Medium": ("#FFFBEB", "#D97706"), "High": ("#FEF2F2", "#DC2626")}
    bg, fg = colors.get(level, ("#F1F5F9", "#475569"))
    return (
        f'<span style="background:{bg};color:{fg};border-radius:6px;'
        f'padding:0.15rem 0.45rem;font-weight:600;font-size:0.82rem">{escape(level)}</span>'
    )


def _guardrails_card_html(rec: dict | None) -> str:
    """Render the Guardrails status card for a call record.

    Pass None to show an empty-state placeholder (used when no call is
    selected from the dashboard).
    """
    if rec is None:
        return """
        <div class="mini-card">
            <p class="mini-title" style="margin:0 0 0.45rem">&#128737;&nbsp; Guardrails</p>
            <div class="hr"></div>
            <div class="muted" style="padding:0.6rem 0;font-size:0.88rem">
                Select a call from the Manager Dashboard to see guardrail results.
                These fields will be populated by the live Guardrail agent.
            </div>
            <div class="hr"></div>
            <div style="font-size:0.76rem;color:#9ca3af;font-style:italic">
                Placeholder &mdash; connect Guardrail agent to populate
            </div>
        </div>
    """

    pii = rec.get("pii_detected", False)
    hallucination = rec.get("hallucination_risk", "Low")
    compliance = rec.get("compliance_risk", "Low")
    confidence = int(round(rec.get("confidence_score", 0.0) * 100))
    review = rec.get("requires_human_review", False)

    review_color = "#DC2626" if review else "#059669"
    review_label = "Required" if review else "Not Required"
    review_icon = "&#9888;" if review else "&#10003;"

    confidence_fill = max(0, min(100, confidence))
    conf_color = (
        "#059669" if confidence_fill >= 80
        else ("#D97706" if confidence_fill >= 60 else "#DC2626")
    )
    conf_bg = (
        "linear-gradient(90deg, #4ade80 0%, #22c55e 100%)" if confidence_fill >= 80
        else ("linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%)" if confidence_fill >= 60
              else "linear-gradient(90deg, #f87171 0%, #ef4444 100%)")
    )

    return f"""
        <div class="mini-card">
            <p class="mini-title" style="margin:0 0 0.45rem">&#128737;&nbsp; Guardrails</p>
            <div class="hr"></div>
            <div class="meta-row">
                <span style="color:#6b7280">PII Detected</span>
                <span>{_bool_indicator(pii, 'Detected', 'Clean')}</span>
            </div>
            <div class="meta-row">
                <span style="color:#6b7280">Hallucination Risk</span>
                <span>{_risk_level_html(hallucination)}</span>
            </div>
            <div class="meta-row">
                <span style="color:#6b7280">Compliance Risk</span>
                <span>{_risk_level_html(compliance)}</span>
            </div>
            <div class="meta-row" style="margin-top:0.55rem">
                <span style="color:#6b7280">Confidence Score</span>
                <span style="font-weight:700;color:{conf_color}">{confidence_fill}%</span>
            </div>
            <div class="progress-track" style="margin-bottom:0.5rem">
                <div style="height:100%;border-radius:999px;background:{conf_bg};width:{confidence_fill}%"></div>
            </div>
            <div class="meta-row">
                <span style="color:#6b7280">Human Review</span>
                <span style="font-weight:600;color:{review_color}">{review_icon}&nbsp;{review_label}</span>
            </div>
            <div class="hr"></div>
            <div style="font-size:0.76rem;color:#9ca3af;font-style:italic">
                Placeholder &mdash; connect Guardrail agent to populate live results
            </div>
        </div>
    """


def _mcp_actions_card_html(rec: dict | None) -> str:
    """Render the MCP Tool Actions card for a call record.

    Pass None to show an empty-state placeholder.
    """
    if rec is None:
        return """
        <div class="mini-card">
            <p class="mini-title" style="margin:0 0 0.45rem">&#128279;&nbsp; MCP Tool Actions</p>
            <div class="hr"></div>
            <div class="muted" style="padding:0.6rem 0;font-size:0.88rem">
                Select a call from the Manager Dashboard to see which MCP tools were invoked.
                These fields will be populated by the live MCP server.
            </div>
            <div class="hr"></div>
            <div style="font-size:0.76rem;color:#9ca3af;font-style:italic">
                Placeholder &mdash; connect MCP server to populate
            </div>
        </div>
    """

    profile = rec.get("customer_profile_checked", False)
    refund = rec.get("refund_policy_checked", False)
    ticket = rec.get("ticket_created", False)
    manager = rec.get("manager_notified", False)

    actions_triggered = sum([profile, refund, ticket, manager])
    total_actions = 4
    pct = int(round(actions_triggered / total_actions * 100))

    return f"""
        <div class="mini-card">
            <p class="mini-title" style="margin:0 0 0.45rem">&#128279;&nbsp; MCP Tool Actions</p>
            <div class="hr"></div>
            <div class="meta-row">
                <span style="color:#6b7280">Customer Profile Checked</span>
                <span>{_bool_indicator(profile)}</span>
            </div>
            <div class="meta-row">
                <span style="color:#6b7280">Refund Policy Checked</span>
                <span>{_bool_indicator(refund)}</span>
            </div>
            <div class="meta-row">
                <span style="color:#6b7280">Ticket Created</span>
                <span>{_bool_indicator(ticket)}</span>
            </div>
            <div class="meta-row">
                <span style="color:#6b7280">Manager Notified</span>
                <span>{_bool_indicator(manager)}</span>
            </div>
            <div class="hr"></div>
            <div class="meta-row" style="margin-bottom:0.3rem">
                <span style="color:#6b7280;font-size:0.84rem">
                    {actions_triggered} of {total_actions} actions triggered
                </span>
                <span style="font-weight:700;color:#4f8bd9">{pct}%</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{pct}%"></div>
            </div>
            <div class="hr" style="margin-top:0.55rem"></div>
            <div style="font-size:0.76rem;color:#9ca3af;font-style:italic">
                Placeholder &mdash; connect MCP server to populate live tool calls
            </div>
        </div>
    """


def render_call_table(records: list[dict]) -> None:
    """Render the call records table: HTML header + per-row (data HTML | View button)."""
    if not records:
        st.markdown(
            '<div class="panel"><div class="muted">No records match the current filters.</div></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        """
        <div class="manager-table-shell">
            <div class="manager-table-header">
                <span class="mc-id">Call ID</span>
                <span class="mc-agent">Agent</span>
                <span class="mc-cust">Customer ID</span>
                <span class="mc-date">Date ↓</span>
                <span class="mc-time">Time</span>
                <span class="mc-dur">Duration</span>
                <span class="mc-qa">QA Score</span>
                <span class="mc-sent">Sentiment</span>
                <span class="mc-esc">Escalation</span>
                <span class="mc-risk">Risk Level</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for rec in records:
        qa_pct = int(round(rec["qa_score"] * 100))
        qa_class = "badge-green" if qa_pct >= 80 else ("badge-yellow" if qa_pct >= 65 else "badge-red")
        escalation_badge = (
            '<span class="badge-red">Yes</span>'
            if rec["escalation_flag"]
            else '<span class="badge-neutral">No</span>'
        )
        date_text, time_text = _format_dashboard_date(rec["datetime"])

        row_html = f"""
        <div class="manager-row">
            <span class="mc-id" style="font-weight:600;color:#2563EB">{escape(rec["call_id"])}</span>
            <span class="mc-agent">{escape(rec["agent_name"])}</span>
            <span class="mc-cust">{escape(rec["customer_id"])}</span>
            <span class="mc-date">{escape(date_text)}</span>
            <span class="mc-time">{escape(time_text)}</span>
            <span class="mc-dur">{escape(rec["duration"])}</span>
            <span class="mc-qa"><span class="{qa_class}">{qa_pct}%</span></span>
            <span class="mc-sent">{_sentiment_badge(rec["sentiment"])}</span>
            <span class="mc-esc">{escalation_badge}</span>
            <span class="mc-risk">{_risk_badge(rec["guardrail_risk"])}</span>
        </div>
        """

        data_col, btn_col = st.columns([0.88, 0.12], gap="small")
        with data_col:
            st.markdown(row_html, unsafe_allow_html=True)
        with btn_col:
            if st.button("View Details ↗", key=f"view_{rec['call_id']}", use_container_width=True):
                st.session_state["selected_call_id"] = rec["call_id"]
                load_selected_call(rec["call_id"])
                st.session_state["current_screen"] = "details"
                st.rerun()

    st.markdown(
        f"""
        <div class="table-footer">
            <span>Showing 1 to {len(records)} of {len(records)} calls</span>
            <span class="pager"><span class="pager-muted">‹</span><span class="pager-active">1</span><span class="pager-muted">›</span></span>
            <span>Rows per page&nbsp;&nbsp;<span class="rows-pill">10⌄</span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_manager_dashboard() -> None:
    """Render the Manager Dashboard — Screen 1."""
    _render_app_sidebar("dashboard")
    st.markdown(
        """
        <div class="page-head">
            <div>
                <h1 class="page-title">Manager Dashboard</h1>
                <div class="page-subtitle">Monitor call center performance and review conversations</div>
            </div>
            <div class="head-actions">
                <div class="head-select">▣&nbsp;&nbsp; Apr 20 – Apr 29, 2026&nbsp;&nbsp;⌄</div>
                <div class="head-user"><div class="head-user-avatar">♙</div><div><strong>Manager</strong><br><span>Team Lead</span></div><span>⌄</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_records = get_mock_call_records()

    # ── KPI Cards ────────────────────────────────────────────────────────────
    total_calls = len(all_records)
    avg_qa = sum(r["qa_score"] for r in all_records) / total_calls if total_calls else 0.0
    escalations = sum(1 for r in all_records if r["escalation_flag"])
    neg_sentiment = sum(1 for r in all_records if r["sentiment"] == "Frustrated")
    risk_calls = sum(1 for r in all_records if r["guardrail_risk"] in ("Medium", "High"))

    kpi_data = [
        ("Total Calls", str(total_calls), "phone", "blue"),
        ("Avg QA Score", f"{int(round(avg_qa * 100))}%", "star", "green"),
        ("Escalations", str(escalations), "trend", "orange"),
        ("Negative Sentiment", str(neg_sentiment), "sad", "red"),
        ("Guardrail Risk Calls", str(risk_calls), "shield", "purple"),
    ]

    kpi_cols = st.columns(5, gap="small")
    for col, (label, value, icon_name, tone) in zip(kpi_cols, kpi_data):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card kpi-{tone}">
                    <div class="kpi-icon">{_icon(icon_name, 34)}</div>
                    <div>
                        <div class="kpi-label">{escape(label)}</div>
                        <div class="kpi-value">{escape(value)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Filters ──────────────────────────────────────────────────────────────
    with st.container():
        st.markdown("<div class='filter-frame-start'></div>", unsafe_allow_html=True)
        fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns([1.4, 1.2, 1, 1.2, 1.2, 0.55, 1.0], gap="small")

        agent_names = ["All Agents"] + sorted({r["agent_name"] for r in all_records})
        with fc1:
            selected_agent = st.selectbox("Agent", agent_names, key="dash_filter_agent")
        dates = ["All Dates"] + sorted({r["datetime"].split(" ")[0] for r in all_records})
        with fc2:
            selected_date = st.selectbox("Date", dates, key="dash_filter_date")
        with fc3:
            qa_min = st.slider("Min QA %", 0, 100, 0, key="dash_filter_qa")
        sentiments = ["All Sentiments", "Neutral", "Happy", "Frustrated"]
        with fc4:
            selected_sentiment = st.selectbox("Sentiment", sentiments, key="dash_filter_sentiment")
        escalation_opts = ["All", "Escalated Only", "Non-Escalated"]
        with fc5:
            selected_escalation = st.selectbox("Escalation", escalation_opts,
                                               key="dash_filter_escalation")
        with fc6:
            st.markdown("<div class='filter-action-pad'></div>", unsafe_allow_html=True)
            st.button("Clear", use_container_width=True, key="dash_clear_filters")
        with fc7:
            st.markdown("<div class='filter-action-pad'></div>", unsafe_allow_html=True)
            st.button("Apply Filters", type="primary", use_container_width=True, key="dash_apply_filters")
        st.markdown("<div class='filter-frame-end'></div>", unsafe_allow_html=True)

    # Apply filters
    filtered = all_records
    if selected_agent != "All Agents":
        filtered = [r for r in filtered if r["agent_name"] == selected_agent]
    if selected_date != "All Dates":
        filtered = [r for r in filtered if r["datetime"].startswith(selected_date)]
    if qa_min > 0:
        filtered = [r for r in filtered if int(round(r["qa_score"] * 100)) >= qa_min]
    if selected_sentiment != "All Sentiments":
        filtered = [r for r in filtered if r["sentiment"] == selected_sentiment]
    if selected_escalation == "Escalated Only":
        filtered = [r for r in filtered if r["escalation_flag"]]
    elif selected_escalation == "Non-Escalated":
        filtered = [r for r in filtered if not r["escalation_flag"]]

    # ── Call Records Table ────────────────────────────────────────────────────
    render_call_table(filtered)


def render_call_detail_view() -> None:
    """Render the AI Call Detail View — Screen 2."""
    # ── Initialise qa_rubric in session state ────────────────────────────────
    if "qa_rubric" not in st.session_state:
        st.session_state["qa_rubric"] = True

    # ── Pending operations ───────────────────────────────────────────────────
    if st.session_state.get("_clear_pending"):
        st.session_state["transcript_input"] = ""
        st.session_state["parsed_transcript"] = ""
        st.session_state["parsed_source"] = ""
        st.session_state["_clear_pending"] = False

    if st.session_state.get("_intake_pending"):
        st.session_state["_intake_pending"] = False
        try:
            with st.spinner("Parsing transcript..."):
                intake_result = _run_intake(
                    api_url=st.session_state["api_url"],
                    session_id=st.session_state["session_id"],
                    customer_id=st.session_state["customer_id"],
                    transcript=st.session_state.get("transcript_input") or None,
                    audio_file=st.session_state.get("audio_file"),
                )
            st.session_state["parsed_transcript"] = intake_result.get("transcript", "")
            st.session_state["transcript_input"] = intake_result.get("transcript", "")
            st.session_state["parsed_source"] = intake_result.get("source", "provided_transcript")
        except Exception as e:
            st.warning(f"Could not auto-parse input: {e}")

    # Resolve current call record for metadata chips
    selected_call_id = st.session_state.get("selected_call_id") or ""
    _all_records = get_mock_call_records()
    _rec: dict | None = next((r for r in _all_records if r["call_id"] == selected_call_id), None)

    # ── Left nav panel (sidebar) ─────────────────────────────────────────────
    _render_app_sidebar("details")

    # ── Main content ─────────────────────────────────────────────────────────
    call_title = f"Call Details \u2013 {selected_call_id}" if selected_call_id else "Call Details"
    agent_name = _rec["agent_name"] if _rec else "\u2014"
    customer_id_disp = _rec["customer_id"] if _rec else "\u2014"
    call_datetime = _rec["datetime"] if _rec else "\u2014"
    call_duration = _rec["duration"] if _rec else "\u2014"
    status_val = _rec.get("status", "Completed") if _rec else "Completed"

    # Breadcrumbs
    st.markdown(
        """
        <div class="cd-breadcrumb">
            <span>Dashboard</span>
            <span class="cd-bc-sep">›</span>
            <span>Call Records</span>
            <span class="cd-bc-sep">›</span>
            <span class="cd-bc-active">Call Details</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Title row with download button
    title_c, dl_c = st.columns([5, 1], gap="small")
    with title_c:
        st.markdown(
            f'<h2 class="cd-page-title">{escape(call_title)}</h2>',
            unsafe_allow_html=True,
        )
    with dl_c:
        st.download_button(
            "⇩ Download",
            data=json.dumps(st.session_state["analysis_result"], indent=2),
            file_name="call_analysis.json",
            mime="application/json",
            use_container_width=True,
            key="cd_header_download",
        )

    # Metadata chips
    status_cls = "cd-chip-status-ok" if status_val == "Completed" else "cd-chip-status-warn"
    st.markdown(
        f"""
        <div class="detail-chips-row">
            {_detail_chip('user', 'Agent', agent_name)}
            {_detail_chip('doc', 'Customer ID', customer_id_disp)}
            {_detail_chip('calendar', 'Date', call_datetime)}
            {_detail_chip('clock', 'Duration', call_duration)}
            {_detail_chip('phone', 'Source', 'Phone Call')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Two-column content ───────────────────────────────────────────────
    transcript_col, analysis_col = st.columns([1.6, 1.4], gap="medium")

    # ── Left: transcript / audio panel ──────────────────────────────────
    with transcript_col:
        st.markdown(_call_audio_card(call_duration), unsafe_allow_html=True)

        parsed = st.session_state.get("parsed_transcript", "")
        rows = _to_transcript_rows(parsed)
        if rows:
            st.markdown(
                f"""
                <div class="ref-transcript-card">
                    <div class="transcript-toolbar">
                        <div class="transcript-tabs">
                            <span class="active">Transcript</span>
                            <span>Timestamps</span>
                            <span>Raw Transcript</span>
                        </div>
                        <div class="transcript-search">Search in transcript... {_icon('search', 16)}</div>
                    </div>
                    <div class="transcript-lines">{_transcript_table_html(rows)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif parsed.strip():
            sentences = re.split(r"(?<=[.!?])\s+", parsed.strip())
            paras = [
                f'<p style="margin:0 0 0.5rem;line-height:1.55;color:#172033">{escape(s.strip())}</p>'
                for s in sentences if s.strip()
            ]
            st.markdown(
                f'<div class="transcript-box" style="max-height:440px;padding:0.85rem 1rem;margin-top:0.45rem">{"".join(paras)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="transcript-box" style="padding:1rem;margin-top:0.45rem">'
                '<span style="color:#94a3b8">No transcript yet. Use Upload to load a file or sample.</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        with st.expander("Input & Processing Options", expanded=False):
            if st.button("Upload", type="primary", use_container_width=True, key="cd_upload_btn"):
                _upload_call_dialog()
            if st.button("Analyze", type="primary", use_container_width=True, key="cd_analyze_btn"):
                try:
                    with st.spinner("Running call analysis..."):
                        result = _run_analysis(
                            api_url=st.session_state["api_url"],
                            session_id=st.session_state["session_id"],
                            customer_id=st.session_state["customer_id"],
                            transcript=st.session_state["transcript_input"],
                            audio_file=st.session_state.get("audio_file"),
                            debug_force_fallback=not st.session_state.get("qa_rubric", True),
                        )
                        st.session_state["analysis_result"] = result
                        st.session_state["kp_escalation"] = result.get("routing", {}).get("used_fallback", False)
                        st.session_state["kp_sentiment"] = _infer_sentiment(result)
                        if result.get("transcript"):
                            st.session_state["parsed_transcript"] = result["transcript"]
                            has_audio = result.get("intake", {}).get("has_audio", False)
                            st.session_state["parsed_source"] = "whisper" if has_audio else "labeled"
                except httpx.HTTPStatusError as e:
                    st.error(f"API error: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
            if st.button("Clear", use_container_width=True, key="cd_clear_btn"):
                st.session_state["analysis_result"] = DEMO_RESULT
                st.session_state["audio_file"] = None
                st.session_state["transcript_input"] = ""
                st.session_state["parsed_transcript"] = ""
                st.session_state["parsed_source"] = ""
                st.rerun()
            st.selectbox("Summary Style", ["Short", "Detailed", "Manager View"], index=1, key="cd_summary_style")
            st.toggle("QA Rubric", key="qa_rubric")
            st.toggle("Show Timestamps", value=True, key="cd_show_timestamps")

        with st.expander("Runtime Settings", expanded=False):
            st.text_input("Session", key="session_id")
            st.text_input("Customer ID", key="customer_id")
            st.text_input("API URL", key="api_url")

    # ── Right: analysis cards ────────────────────────────────────────────
    with analysis_col:
        res = st.session_state["analysis_result"]

        summary = res.get("summary", {})
        routing = res.get("routing", {})
        points = summary.get("key_points", [])
        key_items = [
            ("Customer issue", points[0].replace("Customer issue: ", "") if len(points) > 0 else "Not detected"),
            ("Resolution", points[1].replace("Resolution: ", "") if len(points) > 1 else "Pending review"),
            ("Next step", points[2].replace("Next step: ", "").replace("Next Step: ", "") if len(points) > 2 else "Follow-up required"),
            ("Escalation needed", "Yes" if routing.get("used_fallback", False) else "No"),
            ("Sentiment", _infer_sentiment(res)),
        ]
        key_rows = "".join(f"<li><strong>{escape(k)}:</strong> {escape(v)}</li>" for k, v in key_items)

        st.markdown(
            f"""
            <div class="ref-card summary-wide">
                <div class="ref-card-head">{_icon('doc', 20)}<strong>Summary</strong></div>
                <p>{escape(summary.get('summary', 'No summary generated.'))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        r1c1, r1c2 = st.columns([1.05, 0.95], gap="small")
        with r1c1:
            st.markdown(
                f"""
                <div class="ref-card">
                    <div class="ref-card-head green">{_icon('doc', 20)}<strong>Key Points</strong></div>
                    <ul class="key-list">{key_rows}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with r1c2:
            st.markdown(_qa_detail_html(res), unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2, gap="small")
        with r2c1:
            st.markdown(_actions_card_html(res), unsafe_allow_html=True)
        with r2c2:
            tags = summary.get("tags", [])
            tag_rows = "".join(f"<span class='badge'>{escape(tag)}</span>" for tag in tags[:5])
            st.markdown(
                f"""
                <div class="ref-card">
                    <div class="ref-card-head">{_icon('tag', 20)}<strong>Tags</strong></div>
                    <div class="tag-cloud">{tag_rows}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        _render_workflow(res)

        r3c1, r3c2 = st.columns(2, gap="small")
        with r3c1:
            st.markdown(_guardrails_card_html(_rec), unsafe_allow_html=True)
        with r3c2:
            st.markdown(_mcp_actions_card_html(_rec), unsafe_allow_html=True)

        with st.expander("\u25b6 Raw JSON Output", expanded=False):
            st.download_button(
                "Download JSON",
                data=json.dumps(st.session_state["analysis_result"], indent=2),
                file_name="call_analysis.json",
                mime="application/json",
                key="cd_expander_download",
            )
            st.json(st.session_state["analysis_result"])

        with st.expander("Call Metadata", expanded=False):
            result_meta = st.session_state["analysis_result"]
            intake_m = result_meta.get("intake", {})
            routing_m = result_meta.get("routing", {})
            session_id_m = result_meta.get("session_id", st.session_state["session_id"]) or "—"
            customer_id_m = intake_m.get("customer_id", st.session_state["customer_id"]) or None
            input_type_m = intake_m.get("input_type", "transcript")
            word_count_m = intake_m.get("transcript_word_count", 0)
            route_m = routing_m.get("route", "n/a")
            reason_m = routing_m.get("reason", "")
            fallback_m = routing_m.get("used_fallback", False)

            if _rec:
                st.markdown(
                    f"""
                    <div class="side-group" style="margin-bottom:0.6rem">
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Call ID</span><span style="font-weight:600">{escape(_rec['call_id'])}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Agent</span><span style="font-weight:600">{escape(_rec['agent_name'])}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Customer ID</span><span style="font-weight:600">{escape(_rec['customer_id'])}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Date / Time</span><span style="font-weight:600">{escape(_rec['datetime'])}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Duration</span><span style="font-weight:600">{escape(_rec['duration'])}</span></div>
                    </div>
                    <div class="side-group" style="margin-bottom:0.6rem">
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">PII Detected</span><span style="font-weight:600">{'Yes' if _rec['pii_detected'] else 'No'}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Hallucination Risk</span><span style="font-weight:600">{escape(_rec['hallucination_risk'])}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Compliance Risk</span><span style="font-weight:600">{escape(_rec['compliance_risk'])}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Confidence Score</span><span style="font-weight:600">{int(_rec['confidence_score']*100)}%</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Human Review</span><span style="font-weight:600">{'Yes' if _rec['requires_human_review'] else 'No'}</span></div>
                    </div>
                    <div class="side-group">
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Profile Checked</span><span style="font-weight:600">{'Yes' if _rec['customer_profile_checked'] else 'No'}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Refund Policy</span><span style="font-weight:600">{'Yes' if _rec['refund_policy_checked'] else 'No'}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Ticket Created</span><span style="font-weight:600">{'Yes' if _rec['ticket_created'] else 'No'}</span></div>
                        <div class="meta-row"><span style="color:#64748b;min-width:170px">Manager Notified</span><span style="font-weight:600">{'Yes' if _rec['manager_notified'] else 'No'}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="side-group" style="margin-bottom:0.6rem;margin-top:0.4rem">
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Session ID</span><span style="font-weight:600">{escape(str(session_id_m))}</span></div>
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Customer ID</span><span style="font-weight:600">{escape(str(customer_id_m)) if customer_id_m else '<span style="color:#94a3b8">—</span>'}</span></div>
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Input Type</span><span style="font-weight:600">{escape(str(input_type_m))}</span></div>
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Transcript Words</span><span style="font-weight:600">{word_count_m}</span></div>
                </div>
                <div class="side-group">
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Route</span><span style="font-weight:600">{escape(str(route_m))}</span></div>
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Reason</span><span>{escape(str(reason_m)) if reason_m else '<span style="color:#94a3b8">—</span>'}</span></div>
                    <div class="meta-row"><span style="color:#64748b;min-width:150px">Escalated</span><span style="font-weight:600;color:{'#dc2626' if fallback_m else '#059669'}">{'Yes' if fallback_m else 'No'}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("**Pipeline Trace**")
            st.dataframe(result_meta.get("pipeline_trace", []), use_container_width=True, hide_index=True)


@st.dialog("Upload Call")
def _upload_call_dialog() -> None:
    st.markdown("Choose how to load your call data:")
    mode = st.radio(
        "Input type",
        ["Use Sample", "Transcript File", "Audio File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    uploaded_txt = None
    uploaded_audio = None
    sample_key = None

    if mode == "Use Sample":
        sample_key = st.selectbox("Select a sample call", list(SAMPLE_TRANSCRIPTS.keys()))
        st.caption("The sample transcript will be loaded into the editor for you to review and edit.")
    elif mode == "Transcript File":
        uploaded_txt = st.file_uploader("Upload a .txt transcript", type=["txt"])
    else:
        uploaded_audio = st.file_uploader(
            "Upload an audio file",
            type=["wav", "mp3", "m4a", "ogg"],
        )
        st.caption("Supported formats: WAV, MP3, M4A, OGG. The file will be sent to the transcription API.")

    st.markdown("---")
    col_load, col_cancel = st.columns([1, 1], gap="small")
    with col_load:
        if st.button("Load", type="primary", use_container_width=True):
            if mode == "Use Sample":
                st.session_state["transcript_input"] = SAMPLE_TRANSCRIPTS[sample_key]
                st.session_state["audio_file"] = None
                st.session_state["parsed_transcript"] = SAMPLE_TRANSCRIPTS[sample_key]
                st.session_state["parsed_source"] = "labeled"
                st.rerun()
            elif mode == "Transcript File":
                if uploaded_txt is not None:
                    try:
                        raw = uploaded_txt.read()
                        try:
                            text = raw.decode("utf-8")
                        except UnicodeDecodeError:
                            text = raw.decode("latin-1")
                        st.session_state["transcript_input"] = text
                        st.session_state["audio_file"] = None
                        st.session_state["_intake_pending"] = True
                        st.rerun()
                    except Exception:
                        st.warning("Could not decode file as UTF-8.")
                else:
                    st.warning("Please select a transcript file first.")
            else:
                if uploaded_audio is not None:
                    st.session_state["audio_file"] = uploaded_audio
                    st.session_state["transcript_input"] = ""
                    st.session_state["parsed_transcript"] = ""
                    st.session_state["parsed_source"] = "whisper"
                    st.session_state["_intake_pending"] = True
                    st.rerun()
                else:
                    st.warning("Please select an audio file first.")
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
