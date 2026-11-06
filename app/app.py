"""
CycleScope: Software Dependency Cycle Analyzer
Main Streamlit Application — Developer Dashboard UI
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.cpp_runner import run_analyzer, ensure_binary_compiled
from app.components.overview import render_overview
from app.components.uploader import render_uploader
from app.components.graph_view import render_graph_view
from app.components.kosaraju_view import render_kosaraju_view
from app.components.cycle_view import render_cycle_view
from app.components.condensation_view import render_condensation_view
from app.components.execution_order_view import render_execution_order_view

# Page Configuration
st.set_page_config(
    page_title="CycleScope — Dependency Analyzer",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Developer Tool Styling
st.markdown("""
<style>
    /* Global Base */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #0B1020 !important;
        color: #F1F5F9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    }
    
    /* Top padding reduction */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #101827 !important;
        border-right: 1px solid #273449 !important;
        padding-top: 1rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #273449 !important;
        margin: 0.85rem 0 !important;
    }

    /* Headers */
    .page-header-container {
        margin-bottom: 1.25rem;
        padding-bottom: 0.85rem;
        border-bottom: 1px solid #1E293B;
    }
    .page-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6C8CFF;
        background: rgba(108, 140, 255, 0.12);
        border: 1px solid rgba(108, 140, 255, 0.28);
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 0.4rem;
    }
    .page-header-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #F1F5F9;
        letter-spacing: -0.02em;
        margin: 0 0 0.25rem 0;
    }
    .page-header-desc {
        font-size: 0.88rem;
        color: #94A3B8;
        margin: 0;
        line-height: 1.4;
    }

    /* Cards */
    .metric-card {
        background-color: #151F32;
        border: 1px solid #273449;
        border-radius: 8px;
        padding: 0.95rem 1.15rem;
        transition: border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #3E4F6B;
    }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #94A3B8;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.1;
    }
    .metric-footer {
        margin-top: 0.4rem;
        font-size: 0.74rem;
        color: #64748B;
    }
    .metric-footer.accent { color: #6C8CFF; }
    .metric-footer.danger { color: #F43F5E; }
    .metric-footer.success { color: #34D399; }

    /* Status Indicator */
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin-bottom: 1.1rem;
        font-size: 0.86rem;
    }
    .status-indicator-danger {
        background-color: rgba(244, 63, 94, 0.08);
        border: 1px solid rgba(244, 63, 94, 0.3);
        color: #FECDD3;
    }
    .status-indicator-success {
        background-color: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.3);
        color: #A7F3D0;
    }
    .status-indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .status-indicator-danger .status-indicator-dot {
        background-color: #F43F5E;
        box-shadow: 0 0 6px rgba(244, 63, 94, 0.7);
    }
    .status-indicator-success .status-indicator-dot {
        background-color: #34D399;
        box-shadow: 0 0 6px rgba(52, 211, 153, 0.7);
    }

    /* Dev Card */
    .dev-card {
        background-color: #151F32;
        border: 1px solid #273449;
        border-radius: 6px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.85rem;
    }
    .dev-card-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #F1F5F9;
    }

    /* Code Chips */
    .code-chip {
        display: inline-block;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.78rem;
        background-color: #101827;
        border: 1px solid #273449;
        color: #E2E8F0;
        padding: 2px 7px;
        border-radius: 4px;
        margin: 2px;
    }
    .code-chip.cycle {
        border-color: rgba(244, 63, 94, 0.4);
        background-color: rgba(244, 63, 94, 0.12);
        color: #FECDD3;
    }
    .code-chip.safe {
        border-color: rgba(52, 211, 153, 0.4);
        background-color: rgba(52, 211, 153, 0.12);
        color: #A7F3D0;
    }

    /* Execution Pipeline */
    .pipeline-phase {
        background-color: #151F32;
        border: 1px solid #273449;
        border-radius: 6px;
        padding: 0.85rem 1.1rem;
        transition: border-color 0.2s ease;
    }
    .pipeline-phase:hover {
        border-color: #3E4F6B;
    }
    .pipeline-phase-num {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6C8CFF;
        background: rgba(108, 140, 255, 0.12);
        border: 1px solid rgba(108, 140, 255, 0.28);
        padding: 2px 7px;
        border-radius: 4px;
    }
    .pipeline-connector {
        display: flex;
        justify-content: center;
        color: #475569;
        font-size: 0.85rem;
        margin: -0.25rem 0;
    }

    /* Native Inputs & Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid #273449;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.85rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #6C8CFF !important;
        border-bottom: 2px solid #6C8CFF !important;
        font-weight: 600 !important;
    }
    
    /* Button refinement */
    .stButton > button {
        background-color: #151F32 !important;
        color: #F1F5F9 !important;
        border: 1px solid #273449 !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        border-color: #6C8CFF !important;
        color: #6C8CFF !important;
    }

    /* Sidebar Radio styling */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 0.45rem 0.75rem !important;
        border-radius: 6px !important;
        margin-bottom: 0.15rem !important;
        font-size: 0.85rem !important;
        transition: background-color 0.15s ease, border-left 0.15s ease !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(108, 140, 255, 0.08) !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: rgba(108, 140, 255, 0.14) !important;
        border-left: 3px solid #6C8CFF !important;
        color: #F1F5F9 !important;
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #273449 !important;
        border-radius: 6px !important;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def load_data(csv_text: str):
    """Executes C++ analyzer and caches result in session state."""
    with st.spinner("Analyzing dependency graph with C++ engine..."):
        success, data, error_msg = run_analyzer(csv_text, is_content=True)
        if success:
            st.session_state["graph_data"] = data
            st.session_state["last_error"] = ""
        else:
            st.session_state["graph_data"] = None
            st.session_state["last_error"] = error_msg


def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6C8CFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            <span style="font-size: 1.15rem; font-weight: 700; color: #F1F5F9; letter-spacing: -0.02em;">CycleScope</span>
            <span style="font-size: 0.65rem; font-weight: 600; color: #6C8CFF; background: rgba(108, 140, 255, 0.15); border: 1px solid rgba(108, 140, 255, 0.3); padding: 1px 5px; border-radius: 3px; margin-left: auto;">C++17</span>
        </div>
        <div style="font-size: 0.76rem; color: #64748B; margin-bottom: 1rem;">Software Dependency Cycle Analyzer</div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

        nav_choice = st.radio(
            "Navigation",
            [
                "Overview",
                "Upload Data",
                "Dependency Graph",
                "Kosaraju SCC",
                "Cycle Analysis",
                "Condensed DAG",
                "Execution Order"
            ],
            label_visibility="collapsed"
        )

        st.markdown("<hr style='margin: 1rem 0 0.75rem 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.72rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;'>Quick Actions</div>", unsafe_allow_html=True)

        if st.button("Reset to Default Sample", use_container_width=True):
            sample_file = PROJECT_ROOT / "data" / "sample_dependencies.csv"
            if sample_file.exists():
                st.session_state["active_csv"] = sample_file.read_text()
                load_data(st.session_state["active_csv"])
                st.rerun()

    # Initialize session state if first run
    if "active_csv" not in st.session_state:
        sample_file = PROJECT_ROOT / "data" / "sample_dependencies.csv"
        st.session_state["active_csv"] = sample_file.read_text() if sample_file.exists() else "Module,Depends_On\nA,B\nB,C\nC,A\n"
        load_data(st.session_state["active_csv"])

    # Route navigation
    if nav_choice == "Upload Data":
        new_csv, source_desc = render_uploader()
        if new_csv and new_csv != st.session_state.get("active_csv"):
            st.session_state["active_csv"] = new_csv
            load_data(new_csv)
            st.success(f"Applied dependency records from {source_desc}")

    # Check for errors
    if st.session_state.get("last_error"):
        st.error(f"Error: {st.session_state['last_error']}")
        st.info("Switch to 'Upload Data' in the sidebar to review the CSV format or pick a test fixture.")
        return

    data = st.session_state.get("graph_data")
    if not data:
        st.warning("No graph data available. Please load or upload dependency records.")
        return

    # Render selected view
    if nav_choice == "Overview":
        render_overview(data)
    elif nav_choice == "Upload Data":
        pass  # Handled above
    elif nav_choice == "Dependency Graph":
        render_graph_view(data)
    elif nav_choice == "Kosaraju SCC":
        render_kosaraju_view(data)
    elif nav_choice == "Cycle Analysis":
        render_cycle_view(data)
    elif nav_choice == "Condensed DAG":
        render_condensation_view(data)
    elif nav_choice == "Execution Order":
        render_execution_order_view(data)


if __name__ == "__main__":
    main()
