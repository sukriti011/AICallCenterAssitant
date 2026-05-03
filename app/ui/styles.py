import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            /* ── Design tokens ─────────────────────────────────────────── */
            :root {
                --bg: #f6f8fb;
                --card: #ffffff;
                --panel: #f9fbff;
                --line: #d8e1ee;
                --text-1: #172033;
                --text-2: #64748b;
                --text-3: #94a3b8;
                --blue: #2563eb;
                --blue-soft: #eff6ff;
                --blue-hover: #1d4ed8;
                --green: #059669;
                --green-bg: #ecfdf5;
                --green-border: #a7f3d0;
                --red: #dc2626;
                --red-bg: #fef2f2;
                --red-border: #fca5a5;
                --yellow: #d97706;
                --yellow-bg: #fffbeb;
                --yellow-border: #fde68a;
                --radius: 8px;
            }

            /* ── Base ───────────────────────────────────────────────────── */
            body {
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
                color: var(--text-1);
            }

            [data-testid="stAppViewContainer"] {
                background: var(--bg);
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            /* ── Top header bar ─────────────────────────────────────────── */
            .top-shell {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.5rem 0.9rem;
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.8rem;
            }

            .top-title-wrap {
                display: flex;
                align-items: center;
                gap: 0.6rem;
            }

            .orb {
                width: 26px;
                height: 26px;
                border-radius: 6px;
                background: var(--blue);
                flex-shrink: 0;
            }

            .title {
                font-size: 1rem;
                font-weight: 700;
                letter-spacing: -0.01em;
                margin: 0;
                color: var(--text-1);
            }

            .subtitle {
                margin: 0;
                color: var(--text-2);
                font-size: 0.8rem;
            }

            .top-actions {
                display: flex;
                align-items: center;
                gap: 0.4rem;
                min-width: 300px;
            }

            .top-avatar {
                width: 26px;
                height: 26px;
                border-radius: 50%;
                border: 1px solid var(--line);
                background: var(--panel);
                display: inline-flex;
                align-items: center;
                justify-content: center;
                color: var(--text-2);
                font-size: 0.72rem;
                font-weight: 700;
            }

            /* ── Panels and side groups ─────────────────────────────────── */
            .panel {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.7rem;
                margin-bottom: 0.45rem;
            }

            .side-group {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.7rem;
                margin-bottom: 0.5rem;
            }

            .side-group-title {
                font-size: 0.76rem;
                font-weight: 700;
                color: var(--text-2);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin: 0 0 0.4rem;
            }

            .panel-head {
                font-weight: 700;
                font-size: 0.95rem;
                margin: 0 0 0.4rem;
                color: var(--text-1);
            }

            .muted {
                color: var(--text-2);
                font-size: 0.88rem;
            }

            .segment-title {
                font-weight: 600;
                color: var(--text-1);
                font-size: 0.93rem;
                margin: 0.1rem 0 0.4rem;
            }

            /* ── Transcript ─────────────────────────────────────────────── */
            .transcript-box {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                max-height: 520px;
                overflow-y: auto;
            }

            .row {
                display: grid;
                grid-template-columns: 90px 1fr 68px;
                gap: 0.5rem;
                padding: 0.6rem 0.85rem;
                border-bottom: 1px solid var(--line);
                align-items: start;
            }

            .row:last-child {
                border-bottom: none;
            }

            .speaker {
                color: var(--blue);
                font-weight: 600;
                font-size: 0.88rem;
            }

            .utterance {
                color: var(--text-1);
                font-size: 0.88rem;
                line-height: 1.45;
            }

            .time {
                text-align: right;
                color: var(--text-3);
                font-size: 0.8rem;
            }

            .hl {
                background: #fef9c3;
                border-radius: 3px;
                padding: 0 3px;
            }

            /* ── Analysis cards ─────────────────────────────────────────── */
            .mini-card {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.82rem;
                margin-bottom: 0.5rem;
            }

            .cards-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.6rem;
            }

            .mini-title {
                font-size: 0.7rem;
                font-weight: 700;
                margin: 0 0 0.4rem;
                color: var(--text-2);
                text-transform: uppercase;
                letter-spacing: 0.07em;
            }

            .hr {
                border-top: 1px solid var(--line);
                margin: 0.4rem 0;
            }

            .meta-row {
                display: flex;
                justify-content: space-between;
                gap: 0.5rem;
                margin-bottom: 0.28rem;
                color: var(--text-1);
                font-size: 0.86rem;
            }

            .meta-row span {
                white-space: normal;
                overflow-wrap: anywhere;
            }

            .badge {
                display: inline-block;
                background: var(--blue-soft);
                border: 1px solid #bfdbfe;
                color: var(--blue);
                border-radius: 5px;
                padding: 0.14rem 0.4rem;
                margin: 0.18rem 0.15rem 0 0;
                font-size: 0.75rem;
                font-weight: 600;
            }

            .badge-warm {
                background: var(--yellow-bg);
                border-color: var(--yellow-border);
                color: var(--yellow);
            }

            .badge-neutral {
                background: var(--panel);
                border-color: var(--line);
                color: var(--text-2);
            }

            /* ── Progress bars ──────────────────────────────────────────── */
            .progress-row {
                margin: 0.3rem 0;
            }

            .progress-head {
                display: flex;
                justify-content: space-between;
                color: var(--text-1);
                font-size: 0.86rem;
                margin-bottom: 0.18rem;
            }

            .progress-track {
                width: 100%;
                height: 6px;
                border-radius: 999px;
                background: #e8eef7;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                border-radius: 999px;
                background: var(--blue);
            }

            /* ── Workflow pipeline ──────────────────────────────────────── */
            .workflow {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.65rem 0.82rem;
                margin-top: 0.55rem;
            }

            .workflow-title {
                font-size: 0.7rem;
                font-weight: 700;
                margin: 0 0 0.45rem;
                color: var(--text-2);
                text-transform: uppercase;
                letter-spacing: 0.07em;
            }

            .wf-items {
                display: flex;
                flex-wrap: wrap;
                gap: 0.38rem;
            }

            .wf-pill {
                border: 1px solid var(--green-border);
                background: var(--green-bg);
                color: var(--text-2);
                border-radius: 5px;
                padding: 0.26rem 0.5rem;
                font-size: 0.8rem;
            }

            .wf-pill strong {
                color: var(--green);
            }

            /* ── Input text visibility ──────────────────────────────────── */
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] {
                color: var(--text-1) !important;
                opacity: 1 !important;
            }

            /* Scoped label fix */
            [data-testid="stSelectbox"] label,
            [data-testid="stSlider"] label,
            [data-testid="stTextInput"] label,
            [data-testid="stTextArea"] label {
                color: var(--text-2) !important;
                opacity: 1 !important;
                font-size: 0.76rem !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.04em !important;
            }

            /* Prevent select options from looking disabled */
            [data-baseweb="select"] [data-testid="stMarkdownContainer"],
            [data-baseweb="select"] span,
            [data-baseweb="select"] div[class*="placeholder"] {
                opacity: 1 !important;
            }

            /* ── Buttons ────────────────────────────────────────────────── */
            .stButton > button {
                border-radius: var(--radius);
                border: 1px solid var(--line);
                background: var(--card);
                color: var(--text-1);
                font-weight: 600;
                font-size: 0.845rem;
                min-height: 2rem;
            }

            .stButton > button:hover {
                border-color: #b8c9df;
                background: var(--panel);
            }

            .stDownloadButton > button {
                border-radius: var(--radius);
                border: 1px solid var(--line);
                background: var(--card);
                color: var(--text-1);
                font-weight: 600;
                font-size: 0.83rem;
                min-height: 2rem;
            }

            .stDownloadButton > button:hover {
                border-color: #b8c9df;
                background: var(--panel);
            }

            .stDownloadButton button,
            .stButton button {
                white-space: normal !important;
                line-height: 1.15;
                text-align: center;
            }

            /* Primary — solid cobalt */
            div[data-testid="column"] .stButton button[kind="primary"],
            div[data-testid="stHorizontalBlock"] button[kind="primary"] {
                border-color: var(--blue) !important;
                background: var(--blue) !important;
                color: #ffffff !important;
            }

            div[data-testid="column"] .stButton button[kind="primary"]:hover,
            div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
                background: var(--blue-hover) !important;
                border-color: var(--blue-hover) !important;
            }

            /* ── Tabs — flat underline style ────────────────────────────── */
            button[data-baseweb="tab"] {
                border: none !important;
                border-bottom: 2px solid transparent !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: var(--text-2) !important;
                font-weight: 600 !important;
                font-size: 0.86rem !important;
                padding: 0.55rem 0.95rem !important;
                letter-spacing: 0.01em !important;
            }

            button[data-baseweb="tab"][aria-selected="true"] {
                border-bottom-color: var(--blue) !important;
                color: var(--blue) !important;
                background: transparent !important;
            }

            /* Input field borders */
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"] > div,
            .stFileUploader > div {
                border: 1px solid var(--line) !important;
                border-radius: var(--radius) !important;
                background: var(--card) !important;
            }

            div[data-testid="stMarkdownContainer"] h3,
            div[data-testid="stMarkdownContainer"] p strong {
                color: var(--text-1);
            }

            div[data-testid="stMarkdownContainer"] + div[data-testid="stToggle"] {
                margin-top: 0.1rem;
            }

            [data-baseweb="switch"] [data-testid="stMarkdownContainer"] p {
                color: var(--text-1);
            }

            [data-baseweb="switch"] > div {
                background-color: #c8d5e8 !important;
            }

            [data-baseweb="switch"][aria-checked="true"] > div {
                background-color: var(--blue) !important;
            }

            /* ── Misc helpers ───────────────────────────────────────────── */
            .left-title {
                font-weight: 700;
                color: var(--text-1);
                font-size: 1.1rem;
                margin: 0 0 0.3rem;
            }

            .meta-chip {
                display: inline-block;
                border: 1px solid var(--line);
                background: var(--card);
                color: var(--text-2);
                border-radius: 999px;
                padding: 0.16rem 0.46rem;
                font-size: 0.74rem;
                margin-right: 0.25rem;
                margin-bottom: 0.18rem;
            }

            .header-strip {
                padding: 0.05rem 0 0.35rem;
                margin-bottom: 0.12rem;
            }

            .tab-toolbar {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.26rem 0.38rem;
                margin-bottom: 0.45rem;
            }

            .soft-note {
                color: var(--text-3);
                font-size: 0.82rem;
            }

            .view-more {
                display: inline-block;
                margin-top: 0.55rem;
                margin-left: auto;
                border: 1px solid var(--line);
                border-radius: 5px;
                background: var(--card);
                color: var(--blue);
                padding: 0.24rem 0.5rem;
                font-size: 0.78rem;
                font-weight: 600;
            }

            .bullet-list {
                margin: 0;
                padding-left: 1rem;
            }

            .bullet-list li {
                color: var(--text-2);
                margin-bottom: 0.45rem;
                line-height: 1.5;
            }

            /* ── Responsive ─────────────────────────────────────────────── */
            @media (max-width: 1180px) {
                .top-shell {
                    flex-direction: column;
                    align-items: flex-start;
                }
                .top-actions {
                    width: 100%;
                    min-width: 0;
                }
            }

            @media (max-width: 1000px) {
                .row {
                    grid-template-columns: 68px 1fr 56px;
                }
                .cards-grid {
                    grid-template-columns: 1fr;
                }
            }

            /* ── KPI Cards — left-aligned ───────────────────────────────── */
            .kpi-card {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.8rem 0.95rem 0.65rem;
                text-align: left;
            }

            .kpi-value {
                font-size: 1.65rem;
                font-weight: 700;
                line-height: 1.1;
                margin-bottom: 0.16rem;
                letter-spacing: -0.02em;
            }

            .kpi-label {
                font-size: 0.7rem;
                font-weight: 600;
                color: var(--text-2);
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            /* ── Manager Dashboard table ────────────────────────────────── */
            .manager-table-wrap {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                overflow: hidden;
                background: var(--card);
                margin-bottom: 0.5rem;
            }

            .manager-table-header {
                display: flex;
                align-items: center;
                padding: 0.38rem 0.82rem;
                background: var(--panel);
                border-bottom: 1px solid var(--line);
                font-size: 0.69rem;
                font-weight: 700;
                color: var(--text-2);
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            .manager-row {
                display: flex;
                align-items: center;
                padding: 0.42rem 0.82rem;
                border-bottom: 1px solid var(--line);
                font-size: 0.83rem;
                color: var(--text-1);
                background: var(--card);
                min-height: 2.1rem;
                transition: background 0.1s;
            }

            .manager-row:last-child {
                border-bottom: none;
            }

            .manager-row:hover {
                background: var(--blue-soft);
                cursor: default;
            }

            /* Manager table column widths */
            .mc-id   { flex: 0 0 88px; }
            .mc-agent{ flex: 0 0 118px; }
            .mc-cust { flex: 0 0 88px; color: var(--text-2); font-size: 0.79rem; }
            .mc-date { flex: 0 0 126px; font-size: 0.79rem; }
            .mc-dur  { flex: 0 0 60px; color: var(--text-2); }
            .mc-qa   { flex: 0 0 50px; font-weight: 700; }
            .mc-sent { flex: 0 0 90px; }
            .mc-stat { flex: 0 0 100px; }
            .mc-esc  { flex: 0 0 76px; }
            .mc-risk { flex: 1 0 66px; }
            .mc-act  { flex: 0 0 58px; }

            /* ── Status / risk badges — softer & smaller ────────────────── */
            .badge-green {
                display: inline-block;
                background: var(--green-bg);
                border: 1px solid var(--green-border);
                color: var(--green);
                border-radius: 5px;
                padding: 0.12rem 0.38rem;
                font-size: 0.73rem;
                font-weight: 600;
            }

            .badge-red {
                display: inline-block;
                background: var(--red-bg);
                border: 1px solid var(--red-border);
                color: var(--red);
                border-radius: 5px;
                padding: 0.12rem 0.38rem;
                font-size: 0.73rem;
                font-weight: 600;
            }

            .badge-yellow {
                display: inline-block;
                background: var(--yellow-bg);
                border: 1px solid var(--yellow-border);
                color: var(--yellow);
                border-radius: 5px;
                padding: 0.12rem 0.38rem;
                font-size: 0.73rem;
                font-weight: 600;
            }

            .badge-blue {
                display: inline-block;
                background: var(--blue-soft);
                border: 1px solid #bfdbfe;
                color: var(--blue);
                border-radius: 5px;
                padding: 0.12rem 0.38rem;
                font-size: 0.73rem;
                font-weight: 600;
            }

            /* ── Dashboard filter bar ───────────────────────────────────── */
            .filter-bar {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--card);
                padding: 0.55rem 0.82rem;
                margin-bottom: 0.6rem;
            }

            .filter-bar-title {
                font-size: 0.7rem;
                font-weight: 700;
                color: var(--text-2);
                letter-spacing: 0.06em;
                text-transform: uppercase;
                margin-bottom: 0.32rem;
            }

            .filter-title {
                font-size: 0.7rem;
                font-weight: 700;
                color: var(--text-2);
                letter-spacing: 0.06em;
                text-transform: uppercase;
                margin: 0.65rem 0 0.28rem;
            }

            .stSelectbox label,
            .stSlider label {
                color: var(--text-2) !important;
                font-weight: 600 !important;
                font-size: 0.76rem !important;
            }

            .stSelectbox div[data-baseweb="select"] {
                min-height: 34px !important;
            }

            .stSelectbox div[data-baseweb="select"] * {
                color: var(--text-1) !important;
                opacity: 1 !important;
            }

            .stSelectbox [data-testid="stMarkdownContainer"] p {
                color: var(--text-1) !important;
            }

            .stSlider {
                padding-top: 0.1rem !important;
            }

            .stSlider [data-testid="stTickBar"] {
                display: none !important;
            }

            .stSlider * {
                color: var(--text-1) !important;
                opacity: 1 !important;
            }

            /* ── Transparency overrides ─────────────────────────────────── */
            :not([data-baseweb="modal"]) > [data-baseweb="tab-panel"] {
                background-color: transparent !important;
                background: transparent !important;
                box-shadow: none !important;
            }

            :not([data-baseweb="modal"]) > [data-testid="stHorizontalBlock"],
            :not([data-baseweb="modal"]) > [data-testid="stColumn"],
            [data-testid="stAppViewContainer"] [data-testid="stHorizontalBlock"],
            [data-testid="stAppViewContainer"] [data-testid="stColumn"],
            [data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"]:not([style*="border"]) {
                background-color: transparent !important;
                background: transparent !important;
            }

            [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
                background-color: transparent !important;
                background: transparent !important;
            }

            /* ── Key Points interactive card ────────────────────────────── */
            [data-testid="stAppViewContainer"] div[data-testid="stVerticalBlockBorderWrapper"] {
                border: 1px solid var(--line) !important;
                border-radius: var(--radius) !important;
                background: var(--card) !important;
                box-shadow: none !important;
                margin-bottom: 0.5rem !important;
            }

            [data-testid="stAppViewContainer"] div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
                gap: 0.42rem !important;
            }

            [data-testid="stAppViewContainer"] div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] > div {
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                justify-content: space-between !important;
                width: 100% !important;
            }

            [data-testid="stAppViewContainer"] div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] {
                margin-bottom: 0.1rem !important;
            }

            [data-testid="stAppViewContainer"] div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] {
                margin-bottom: 0.1rem !important;
            }

            /* ── Dialog overrides ───────────────────────────────────────── */
            [data-baseweb="modal"] [data-testid="stVerticalBlock"],
            [data-baseweb="modal"] [data-testid="stHorizontalBlock"],
            [data-baseweb="modal"] [data-testid="stColumn"],
            [data-baseweb="modal"] [data-testid="stMarkdownContainer"] {
                background-color: unset !important;
                background: unset !important;
            }

            [data-baseweb="modal"] div[data-testid="stVerticalBlockBorderWrapper"] {
                border: none !important;
                border-radius: unset !important;
                background: unset !important;
                box-shadow: none !important;
                margin-bottom: unset !important;
            }

            [data-baseweb="modal"] button[kind="primary"] {
                border-color: var(--blue) !important;
                background: var(--blue) !important;
                color: #ffffff !important;
            }

            [data-baseweb="modal"] button[kind="secondary"] {
                border: 1px solid var(--line) !important;
                background: var(--card) !important;
                color: var(--text-1) !important;
            }

            /* ── Call Details nav panel ─────────────────────────────────── */
            .cd-nav {
                border: 1px solid var(--line); border-radius: var(--radius);
                background: var(--card); padding: 0.65rem 0.45rem;
                display: flex; flex-direction: column; gap: 0.15rem;
            }
            .cd-nav-logo {
                display: flex; align-items: center; gap: 0.45rem;
                padding: 0.2rem 0.45rem 0.6rem; border-bottom: 1px solid var(--line);
                margin-bottom: 0.45rem;
            }
            .cd-nav-brand { font-size: 0.82rem; font-weight: 700; color: var(--text-1); white-space: nowrap; }
            .cd-nav-section {
                font-size: 0.6rem; font-weight: 700; color: var(--text-3);
                letter-spacing: 0.09em; text-transform: uppercase; padding: 0 0.45rem; margin-bottom: 0.15rem;
            }
            .cd-nav-item {
                display: flex; align-items: center; gap: 0.45rem;
                padding: 0.38rem 0.5rem; border-radius: 6px;
                font-size: 0.82rem; font-weight: 500; color: var(--text-2);
            }
            .cd-nav-item:hover { background: var(--panel); color: var(--text-1); }
            .cd-nav-active { background: var(--blue-soft); color: var(--blue) !important; font-weight: 600; }
            .cd-nav-icon { width: 15px; text-align: center; font-size: 0.88rem; flex-shrink: 0; }

            /* ── Profile row ──────────────────────────────────────────────── */
            .cd-profile-row {
                display: flex; align-items: center; gap: 0.35rem;
                padding: 0.5rem 0.45rem; border-top: 1px solid var(--line); margin-top: 0.35rem;
            }
            .cd-avatar {
                width: 28px; height: 28px; border-radius: 50%; background: var(--blue);
                color: #fff; font-size: 0.68rem; font-weight: 700;
                display: inline-flex; align-items: center; justify-content: center;
                flex-shrink: 0; position: relative;
            }
            .cd-avatar::after {
                content: ''; width: 7px; height: 7px; border-radius: 50%;
                background: #22c55e; border: 2px solid #fff;
                position: absolute; bottom: -1px; right: -1px;
            }
            .cd-profile-info { flex: 1; min-width: 0; overflow: hidden; }
            .cd-profile-name { font-size: 0.76rem; font-weight: 600; color: var(--text-1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .cd-profile-role { font-size: 0.68rem; color: var(--text-2); }
            .cd-bell, .cd-chevron { font-size: 0.85rem; color: var(--text-2); flex-shrink: 0; }

            /* ── Breadcrumbs ──────────────────────────────────────────────── */
            .cd-breadcrumb {
                font-size: 0.76rem; color: var(--text-2); margin-bottom: 0.3rem;
                display: flex; align-items: center; gap: 0.28rem;
            }
            .cd-bc-sep { color: var(--text-3); }
            .cd-bc-active { color: var(--blue); font-weight: 600; }

            /* ── Page title & chips ───────────────────────────────────────── */
            .cd-page-title { font-size: 1.18rem; font-weight: 700; color: var(--text-1); margin: 0 0 0.45rem; letter-spacing: -0.01em; }
            .cd-chips-row { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.65rem; }
            .cd-chip {
                display: inline-flex; align-items: center; border: 1px solid var(--line);
                border-radius: 5px; background: var(--panel); color: var(--text-1);
                font-size: 0.76rem; padding: 0.18rem 0.48rem; white-space: nowrap; gap: 0.18rem;
            }
            .cd-chip-status-ok { background: var(--green-bg); border-color: var(--green-border); color: var(--green); font-weight: 600; }
            .cd-chip-status-warn { background: var(--red-bg); border-color: var(--red-border); color: var(--red); font-weight: 600; }

            /* ── Panel section title ──────────────────────────────────────── */
            .cd-panel-title { font-size: 0.7rem; font-weight: 700; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.4rem; }

            /* ── Agent Workflow Trace card ────────────────────────────────── */
            .wf-trace-card { border: 1px solid var(--line); border-radius: var(--radius); background: var(--card); padding: 0.72rem 0.9rem; margin-top: 0.5rem; margin-bottom: 0.5rem; }
            .wf-trace-head { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.65rem; }
            .wf-icon { font-size: 0.95rem; }
            .wf-trace-title { font-size: 0.7rem; font-weight: 700; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.07em; }
            .wf-trace-steps { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 0; }
            .wf-box { border: 1px solid var(--line); border-radius: 6px; background: var(--panel); padding: 0.32rem 0.5rem; min-width: 85px; text-align: center; }
            .wf-box-total { background: var(--blue-soft) !important; border-color: #bfdbfe !important; }
            .wf-box-label { font-size: 0.7rem; font-weight: 600; color: var(--text-1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .wf-box-time { font-size: 0.66rem; color: var(--text-2); margin-top: 0.08rem; }
            .wf-arrow { color: var(--text-3); font-size: 0.88rem; padding: 0 0.28rem; flex-shrink: 0; }

            /* ── Reference screen alignment overrides ───────────────────── */
            [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
            [data-testid="stSidebar"] {
                background: #ffffff;
                border-right: 1px solid #dbe4f0;
                min-width: 250px !important;
                width: 250px !important;
            }
            [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
                padding: 1.2rem 0.75rem 1rem;
                display: flex;
                flex-direction: column;
                gap: 0;
            }
            .block-container {
                max-width: 1540px;
                padding: 1.5rem 1.5rem 1rem;
            }
            .main .block-container { color: #071a44; }
            .ui-icon { flex-shrink: 0; }

            /* ── Sidebar brand ───────────────────────────────────────────── */
            .side-brand {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                margin: 0 0 1.2rem 0.1rem;
            }
            .side-logo-img {
                width: 44px;
                height: 44px;
                border-radius: 10px;
                object-fit: cover;
                flex-shrink: 0;
            }
            .side-logo-fallback {
                width: 44px;
                height: 44px;
                border-radius: 12px;
                background: #eaf2ff;
                border: 1px solid #cfe0ff;
                flex-shrink: 0;
            }
            .side-brand-text {
                font-size: 1.0rem;
                line-height: 1.25;
                font-weight: 800;
                letter-spacing: -0.01em;
            }
            .side-brand-text span { color: #005DFF; }

            /* ── Sidebar nav — Streamlit button overrides ────────────────── */
            /* Collapse the zero-height marker divs */
            [data-testid="stSidebar"] .element-container:has(.sidenav-marker),
            [data-testid="stSidebar"] .element-container:has(.sidenav-active-marker) {
                height: 0 !important;
                min-height: 0 !important;
                overflow: hidden !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            /* Remove gap between hidden marker and its button */
            [data-testid="stSidebar"] .element-container:has(.sidenav-marker) + .element-container,
            [data-testid="stSidebar"] .element-container:has(.sidenav-active-marker) + .element-container {
                margin-top: 0 !important;
            }
            /* All sidebar nav buttons */
            [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                border-radius: 8px !important;
                text-align: left !important;
                justify-content: flex-start !important;
                padding: 0 0.9rem !important;
                min-height: 48px !important;
                font-size: 0.93rem !important;
                font-weight: 600 !important;
                color: #16294f !important;
                width: 100% !important;
                transition: background 0.1s !important;
            }
            [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
                background: #f1f5f9 !important;
                color: #071a44 !important;
            }
            /* Active nav item — element immediately after the active marker */
            [data-testid="stSidebar"] .element-container:has(.sidenav-active-marker) + .element-container button[data-testid="stBaseButton-secondary"] {
                background: #eaf2ff !important;
                color: #005DFF !important;
                box-shadow: inset 4px 0 0 #0b63ff !important;
                font-weight: 700 !important;
            }
            /* "Back to Dashboard" button styling */
            [data-testid="stSidebar"] .element-container:has(.sidenav-back-spacer) + .element-container button[data-testid="stBaseButton-secondary"] {
                color: #64748b !important;
                font-size: 0.84rem !important;
                font-weight: 600 !important;
                min-height: 38px !important;
                border-top: 1px solid #e2eaf4 !important;
                border-radius: 0 !important;
                padding: 0 0.9rem !important;
                margin-top: 0.5rem !important;
            }
            /* Hide the back-spacer marker */
            [data-testid="stSidebar"] .element-container:has(.sidenav-back-spacer) {
                height: 0 !important;
                min-height: 0 !important;
                overflow: hidden !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            [data-testid="stSidebar"] .element-container:has(.sidenav-back-spacer) + .element-container {
                margin-top: 0 !important;
            }

            /* ── Sidebar footer & profile ────────────────────────────────── */
            .side-footer {
                padding: 0 0.2rem 0.8rem;
                color: #7a8aa8;
                font-size: 0.76rem;
                line-height: 1.45;
                margin-top: 0.5rem;
            }
            .side-profile {
                border-top: 1px solid #dbe4f0;
                display: flex;
                align-items: center;
                gap: 0.7rem;
                padding: 0.8rem 0.15rem 0.2rem;
            }
            .side-avatar, .head-user-avatar {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: #0b63ff;
                color: #ffffff;
                font-weight: 800;
                font-size: 0.82rem;
                position: relative;
                flex-shrink: 0;
            }
            .side-avatar::after {
                content: "";
                position: absolute;
                width: 9px;
                height: 9px;
                border-radius: 50%;
                background: #16c47f;
                border: 2px solid #fff;
                right: -1px;
                bottom: -1px;
            }
            .side-profile-name { font-weight: 700; font-size: 0.87rem; }
            .side-profile-role { color: #64748b; font-size: 0.75rem; }
            .side-profile-spacer { flex: 1; }
            .side-bell { color: #071a44; }

            .page-head {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 1rem;
                margin-bottom: 1.4rem;
            }
            .page-title {
                font-size: 2.3rem;
                line-height: 1;
                margin: 0 0 0.4rem;
                color: #071a44;
                letter-spacing: 0;
                font-weight: 800;
            }
            .page-subtitle {
                color: #5b6b84;
                font-size: 0.95rem;
            }
            .head-actions {
                display: flex;
                align-items: center;
                gap: 0.9rem;
            }
            .head-select, .head-user {
                height: 48px;
                border: 1px solid #d5deeb;
                border-radius: 7px;
                background: #fff;
                display: flex;
                align-items: center;
                gap: 0.7rem;
                padding: 0 0.9rem;
                color: #17264a;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            }
            .head-user strong { font-size: 0.88rem; }
            .head-user span { color: #64748b; font-size: 0.78rem; }
            .head-user-avatar {
                background: #dbeafe;
                color: #0b63ff;
            }

            .kpi-card {
                min-height: 90px;
                display: flex;
                align-items: center;
                gap: 1rem;
                border: 1px solid #e2eaf4;
                border-radius: 10px;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
                margin-bottom: 1rem;
                padding: 0.85rem 1rem;
            }
            .kpi-card .kpi-icon {
                width: 52px;
                height: 52px;
                border-radius: 10px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
            .kpi-card .kpi-label {
                font-size: 0.82rem;
                text-transform: none;
                letter-spacing: 0;
                color: #53627a;
                margin-bottom: 0.12rem;
            }
            .kpi-card .kpi-value {
                font-size: 1.7rem;
                letter-spacing: 0;
                color: #071a44;
            }
            .kpi-blue .kpi-icon { background: #eaf2ff; color: #0b63ff; }
            .kpi-green .kpi-icon { background: #e9f8ef; color: #16834d; }
            .kpi-orange .kpi-icon { background: #fff3d8; color: #f59e0b; }
            .kpi-red .kpi-icon { background: #feecee; color: #dc2626; }
            .kpi-purple .kpi-icon { background: #f1edff; color: #5b35d5; }
            .kpi-green .kpi-value { color: #16834d; }
            .kpi-orange .kpi-value { color: #c97900; }
            .kpi-red .kpi-value { color: #dc2626; }
            .kpi-purple .kpi-value { color: #5b35d5; }

            .filter-frame-start {
                border: 1px solid #e2eaf4;
                border-bottom: 0;
                border-radius: 10px 10px 0 0;
                background: #fff;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
                margin-top: 0.3rem;
                padding: 0.55rem 1rem 0.35rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .filter-frame-start span {
                font-size: 0.7rem;
                font-weight: 700;
                color: #53627a;
                text-transform: uppercase;
                letter-spacing: 0.07em;
            }
            .filter-frame-end {
                border: 1px solid #e2eaf4;
                border-top: 0;
                border-radius: 0 0 10px 10px;
                height: 0.6rem;
                background: #fff;
                margin-bottom: 1rem;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
            }
            .filter-spacer { height: 0.25rem; }
            .filter-action-pad { height: 1.28rem; }

            .manager-table-shell {
                border: 1px solid #e2eaf4;
                border-radius: 10px 10px 0 0;
                overflow: hidden;
                background: #fff;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
            }
            .manager-table-header, .manager-row {
                display: flex;
                align-items: center;
                padding: 0.6rem 1.1rem;
                min-height: 40px;
            }
            .manager-table-header {
                background: #f8fafc;
                border-bottom: 1px solid #e2eaf4;
                color: #64748b;
                text-transform: none;
                letter-spacing: 0;
                font-size: 0.79rem;
                font-weight: 600;
            }
            .manager-row {
                border: 1px solid #e2eaf4;
                border-top: 0;
                border-radius: 0;
                background: #fff;
                font-size: 0.84rem;
                min-height: 46px;
                transition: background 0.12s;
            }
            .manager-row:hover { background: #f8fafc; }
            .mc-id { flex: 0 0 100px; }
            .mc-agent { flex: 0 0 140px; }
            .mc-cust { flex: 0 0 108px; }
            .mc-date { flex: 0 0 108px; }
            .mc-time { flex: 0 0 86px; }
            .mc-dur { flex: 0 0 80px; }
            .mc-qa { flex: 0 0 90px; }
            .mc-sent { flex: 0 0 120px; }
            .mc-esc { flex: 0 0 90px; }
            .mc-risk { flex: 1 0 90px; }
            .badge-green, .badge-red, .badge-yellow, .badge-neutral, .badge, .badge-blue {
                border-radius: 999px;
                padding: 0.22rem 0.68rem;
                font-size: 0.76rem;
                font-weight: 700;
            }
            .badge-neutral {
                display: inline-block;
                background: #f1f5f9;
                border: 1px solid #e2eaf4;
                color: #64748b;
            }
            :not([data-testid="stSidebar"]) div[data-testid="column"] .stButton button {
                min-height: 34px;
                border-radius: 8px;
                color: #005DFF;
                border-color: #0b63ff;
                background: #ffffff;
                font-weight: 600;
            }
            :not([data-testid="stSidebar"]) div[data-testid="column"] .stButton button:hover {
                background: #eff6ff !important;
            }

            /* ── Dashboard section heading ───────────────────────────── */
            .dash-section-head {
                display: flex;
                align-items: center;
                gap: 0.65rem;
                margin: 0.6rem 0 0.55rem;
            }
            .dash-section-title {
                font-size: 1.1rem;
                font-weight: 700;
                color: #071a44;
                margin: 0;
            }
            .dash-count-badge {
                background: #eff6ff;
                color: #0b63ff;
                border: 1px solid #bfdbfe;
                border-radius: 999px;
                padding: 0.1rem 0.6rem;
                font-size: 0.76rem;
                font-weight: 700;
            }
            .table-footer {
                min-height: 46px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                border: 1px solid #e2eaf4;
                border-top: 0;
                border-radius: 0 0 10px 10px;
                background: #fff;
                padding: 0 1.1rem;
                color: #394963;
                font-size: 0.82rem;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            }
            .pager { display: flex; align-items: center; gap: 0.45rem; }
            .pager-muted, .pager-active, .rows-pill {
                border: 1px solid #d9e3ef;
                border-radius: 6px;
                min-width: 32px;
                height: 32px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: #fff;
            }
            .pager-active {
                background: #0b63ff;
                color: #fff;
                border-color: #0b63ff;
            }
            .rows-pill { min-width: 58px; }

            .cd-breadcrumb {
                color: #64748b;
                font-weight: 500;
                margin-bottom: 0.3rem;
                font-size: 0.8rem;
            }
            .cd-page-title {
                font-size: 1.55rem;
                line-height: 1.1;
                color: #071a44;
                margin-bottom: 0.35rem;
            }
            .detail-chips-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 0.6rem;
            }
            .detail-chip {
                min-height: 28px;
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                border: 1px solid #d9e3ef;
                background: #fff;
                border-radius: 5px;
                padding: 0 0.6rem;
                color: #071a44;
                font-size: 0.78rem;
            }
            .detail-chip .ui-icon { color: #0b63ff; }
            .detail-chip strong { font-weight: 700; }
            .detail-chip span { color: #273a5e; }

            .audio-card, .ref-transcript-card, .ref-card {
                border: 1px solid #d9e3ef;
                border-radius: 8px;
                background: #fff;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            }
            .audio-card {
                padding: 0.7rem 0.9rem;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }
            .card-title {
                font-size: 0.88rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            .audio-row {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                color: #071a44;
                font-size: 0.82rem;
            }
            .play-button {
                width: 36px;
                height: 42px;
                border-radius: 50%;
                border: 0;
                background: #0b63ff;
                color: #fff;
                font-size: 1rem;
            }
            .waveform {
                flex: 1;
                height: 38px;
                display: flex;
                align-items: center;
                gap: 3px;
                overflow: hidden;
            }
            .waveform span {
                display: block;
                width: 3px;
                height: 22px;
                border-radius: 999px;
                background: #0b63ff;
            }
            .waveform span:nth-child(2n) { height: 30px; opacity: 0.85; }
            .waveform span:nth-child(3n) { height: 16px; opacity: 0.7; }
            .waveform .wave-muted { background: #cbd5e1; }
            .audio-icon { color: #071a44; font-size: 1.15rem; }

            .ref-transcript-card {
                border-top-left-radius: 0;
                border-top-right-radius: 0;
                max-height: 420px;
                overflow: hidden;
            }
            .transcript-toolbar {
                min-height: 48px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.75rem;
                border-bottom: 1px solid #d9e3ef;
                padding: 0 0.85rem;
            }
            .transcript-tabs {
                display: flex;
                align-items: stretch;
                align-self: stretch;
                gap: 1rem;
                font-size: 0.82rem;
                font-weight: 700;
            }
            .transcript-tabs span {
                display: flex;
                align-items: center;
                color: #17264a;
                border-bottom: 3px solid transparent;
            }
            .transcript-tabs .active {
                color: #0b63ff;
                border-bottom-color: #0b63ff;
            }
            .transcript-search {
                border: 1px solid #d9e3ef;
                border-radius: 6px;
                height: 30px;
                min-width: 180px;
                padding: 0 0.6rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                color: #7a8aa8;
                font-size: 0.76rem;
            }
            .transcript-lines {
                max-height: 340px;
                overflow: auto;
                padding: 0.2rem 0.85rem;
            }
            .transcript-line {
                display: grid;
                grid-template-columns: 52px 100px 1fr;
                align-items: center;
                gap: 0.6rem;
                min-height: 36px;
                border-bottom: 1px solid #e4ebf3;
                color: #071a44;
                font-size: 0.8rem;
            }
            .transcript-time { font-weight: 600; color: #122a5c; }
            .speaker-pill {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.2rem;
                border-radius: 6px;
                min-height: 22px;
                font-size: 0.72rem;
                font-weight: 700;
            }
            .speaker-agent {
                background: #eaf2ff;
                color: #005DFF;
                border: 1px solid #cfe0ff;
            }
            .speaker-customer {
                background: #e9f8ef;
                color: #087a42;
                border: 1px solid #bdebd0;
            }
            .transcript-copy {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .ref-card {
                padding: 0.7rem 0.85rem;
                min-height: 0;
                margin-bottom: 0.5rem;
            }
            .summary-wide {
                min-height: 0;
                margin-bottom: 0.5rem;
            }
            .ref-card-head {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #071a44;
                margin-bottom: 0.55rem;
                font-size: 0.88rem;
            }
            .ref-card-head .ui-icon {
                width: 28px;
                height: 28px;
                padding: 5px;
                border-radius: 50%;
                background: #eef2ff;
                color: #0b63ff;
            }
            .ref-card-head.green .ui-icon {
                background: #e9f8ef;
                color: #16a34a;
            }
            .summary-wide p {
                color: #17264a;
                line-height: 1.55;
                max-width: 720px;
                font-size: 0.86rem;
                margin: 0;
            }
            .key-list {
                margin: 0;
                padding-left: 1.2rem;
                color: #17264a;
                line-height: 1.75;
                font-size: 0.86rem;
            }
            .key-list li::marker { color: #0b63ff; }
            .qa-ref-card { min-height: 0; }
            .qa-overall {
                margin-left: auto;
                color: #16a34a;
                font-size: 1.45rem;
                font-weight: 800;
            }
            .qa-line { margin: 0.38rem 0; }
            .qa-line > div:first-child {
                display: flex;
                justify-content: space-between;
                color: #071a44;
                font-size: 0.78rem;
                margin-bottom: 0.18rem;
            }
            .qa-track {
                height: 4px;
                border-radius: 999px;
                background: #e7edf5;
                overflow: hidden;
            }
            .qa-track div { height: 100%; border-radius: 999px; }
            .tag-cloud { display: flex; flex-wrap: wrap; gap: 0.5rem; }

            .wf-trace-card {
                padding: 0.65rem 0.85rem;
                margin-top: 0;
                margin-bottom: 0.5rem;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
            }
            .wf-box {
                min-width: 80px;
                min-height: 52px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                background: #fff;
            }
            .wf-box-label {
                white-space: normal;
                font-size: 0.68rem;
            }
            .wf-box-time { font-weight: 700; color: #071a44; }

            @media (max-width: 1180px) {
                .page-head, .head-actions { flex-direction: column; align-items: stretch; }
                .transcript-line { grid-template-columns: 48px 100px 1fr; }
                .transcript-copy { white-space: normal; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
