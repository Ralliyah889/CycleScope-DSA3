"""
Data Uploader & Dataset Selection Component
Allows users to upload custom CSVs, pick pre-built test scenarios, or edit data interactively.
"""

import streamlit as st
from pathlib import Path
from typing import Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

PRESETS = {
    "Standard Sample (3-Node Cycle + Chain)": "sample_dependencies.csv",
    "Clean Architecture (No Cycles - Pure DAG)": "no_cycles.csv",
    "Multiple Circular Groups (2 Distinct Cycles)": "multiple_cycles.csv",
    "Self-Loop Cycle (Recursive Dependency)": "self_loop.csv",
    "Disconnected Clusters & Standalone Modules": "disconnected.csv",
}


def render_uploader() -> Tuple[str, str]:
    """
    Renders dataset selection, file uploader, and interactive CSV editor.
    Returns: (csv_content: str, source_description: str)
    """
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">INPUT DATA</span>
        <h1 class="page-header-title">Dependency Data Management</h1>
        <p class="page-header-desc">Import software module dependencies via CSV, select test fixtures, or modify raw records.</p>
    </div>
    """, unsafe_allow_html=True)

    # Preset selection & Download template
    col_preset, col_dl = st.columns([3, 1])

    with col_preset:
        preset_choice = st.selectbox(
            "Select Scenario / Test Fixture:",
            list(PRESETS.keys()),
            index=0,
            help="Pre-configured graph topologies representing standard real-world cases."
        )

    with col_dl:
        sample_path = DATA_DIR / "sample_dependencies.csv"
        sample_text = sample_path.read_text() if sample_path.exists() else "Module,Depends_On\nA,B\nB,C\nC,A\n"
        st.download_button(
            label="Download Sample CSV",
            data=sample_text,
            file_name="sample_dependencies.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Tabs for Active Preset, Upload CSV, Direct Editor
    tab_preset, tab_upload, tab_editor = st.tabs(["Active Fixture", "Upload Custom CSV", "Raw CSV Editor"])

    active_csv = ""
    source_name = ""

    with tab_preset:
        filename = PRESETS[preset_choice]
        preset_file = DATA_DIR / filename
        if preset_file.exists():
            active_csv = preset_file.read_text()
            source_name = f"Fixture: {preset_choice}"
            st.caption(f"Loaded from <code>data/{filename}</code>")
            st.code(active_csv, language="csv")
        else:
            st.error(f"Preset file not found: {filename}")

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload Dependency CSV File",
            type=["csv", "txt"],
            help="Expected header: Module,Depends_On"
        )
        if uploaded_file is not None:
            try:
                active_csv = uploaded_file.getvalue().decode("utf-8")
                source_name = f"Upload: {uploaded_file.name}"
                st.success(f"Parsed uploaded file: {uploaded_file.name}")
                st.code(active_csv, language="csv")
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")

    with tab_editor:
        st.caption("Directly modify or paste CSV dependency lines below:")
        edited_csv = st.text_area(
            "CSV Content (Format: Module,Depends_On)",
            value=active_csv if active_csv else "Module,Depends_On\nA,B\nB,C\nC,A\n",
            height=180,
            key="csv_text_editor"
        )
        if st.button("Apply Changes", use_container_width=False):
            active_csv = edited_csv
            source_name = "Direct Editor"

    # CSV Format Guidelines
    with st.expander("CSV Format Specifications"):
        st.markdown("""
        - **Header:** `Module,Depends_On` (optional, automatically parsed).
        - **Standalone / Root modules:** Set `Depends_On` to `none`, `-`, or empty (e.g. `Database,none`).
        - **Multiple prerequisites:** Provide multiple lines with the same module name (e.g., `App,Database` and `App,Logger`).
        - **Comments:** Lines starting with `#` are ignored.
        """)

    return active_csv, source_name
