import os
import sys

import streamlit as st

# Ensure app/ui/ is importable regardless of CWD when running via streamlit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mock_data import DEMO_RESULT, SAMPLE_TRANSCRIPTS
from styles import apply_styles
from components import (
    _infer_sentiment,
    load_selected_call,
    render_manager_dashboard,
    render_call_detail_view,
)

API_BASE_URL = os.getenv("CALL_CENTER_API_BASE_URL", "http://localhost:8000/api/v1/call-center")
PAGE_TITLE = "AI Call Center Assistant"


def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="phone", layout="wide")
    apply_styles()

    # ── Session state initialisation ─────────────────────────────────────────
    if "current_screen" not in st.session_state:
        st.session_state["current_screen"] = "dashboard"
    if "selected_call_id" not in st.session_state:
        st.session_state["selected_call_id"] = None
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = DEMO_RESULT
    if "api_url" not in st.session_state:
        st.session_state["api_url"] = API_BASE_URL
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = "demo-session-001"
    if "customer_id" not in st.session_state:
        st.session_state["customer_id"] = ""
    if "transcript_input" not in st.session_state:
        st.session_state["transcript_input"] = SAMPLE_TRANSCRIPTS["Billing Dispute"]
    if "audio_file" not in st.session_state:
        st.session_state["audio_file"] = None
    if "parsed_transcript" not in st.session_state:
        st.session_state["parsed_transcript"] = SAMPLE_TRANSCRIPTS["Billing Dispute"]
    if "parsed_source" not in st.session_state:
        st.session_state["parsed_source"] = "labeled"
    if "_clear_pending" not in st.session_state:
        st.session_state["_clear_pending"] = False
    if "_intake_pending" not in st.session_state:
        st.session_state["_intake_pending"] = False
    if "kp_escalation" not in st.session_state:
        st.session_state["kp_escalation"] = DEMO_RESULT.get("routing", {}).get("used_fallback", False)
    if "kp_sentiment" not in st.session_state:
        st.session_state["kp_sentiment"] = _infer_sentiment(DEMO_RESULT)

    # ── Screen router ────────────────────────────────────────────────────────
    if st.session_state["current_screen"] == "dashboard":
        render_manager_dashboard()
    elif st.session_state["current_screen"] == "details":
        if st.session_state.get("selected_call_id"):
            load_selected_call(st.session_state["selected_call_id"])
        render_call_detail_view()
    else:
        st.session_state["current_screen"] = "dashboard"
        st.rerun()


if __name__ == "__main__":
    main()
