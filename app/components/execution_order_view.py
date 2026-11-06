"""
Execution Order & Topological Sorting Component
Displays a clean vertical execution pipeline, parallel-safe phase cards,
interactive Kahn stepper, and collapsible theory notes.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from app.utils.graph_visualizer import generate_kahn_step_dot


def render_execution_order_view(data: Dict[str, Any]):
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">EXECUTION ORDER</span>
        <h1 class="page-header-title">Topological Execution Pipeline</h1>
        <p class="page-header-desc">Multi-phase dependency resolution computed via Kahn's in-degree topological sort algorithm on the condensation DAG.</p>
    </div>
    """, unsafe_allow_html=True)

    topo = data.get("topological_sort", {})
    is_dag = topo.get("is_dag", True)
    phases = topo.get("phases", [])
    kahn_steps = topo.get("kahn_steps", [])

    if not is_dag:
        st.error("Cannot compute topological execution order: cycle present in Condensation Graph.")
        return

    tab_pipe, tab_stepper = st.tabs(["Execution Pipeline", "Kahn's Stepper & Graph State"])

    # ==========================================
    # TAB 1: Execution Pipeline
    # ==========================================
    with tab_pipe:
        st.markdown(f"<div style='font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.75rem;'>Phased Execution Schedule ({len(phases)} Phase{'s' if len(phases) != 1 else ''})</div>", unsafe_allow_html=True)

        for i, phase in enumerate(phases):
            p_num = phase.get("phase_number")
            p_mods = phase.get("modules", [])
            p_sccs = phase.get("scc_ids", [])
            has_cyc = phase.get("contains_cycles", False)
            expl = phase.get("explanation", "")

            badge_text = "CONTAINS CYCLES" if has_cyc else "PARALLEL SAFE"
            badge_bg = "rgba(244, 63, 94, 0.12)" if has_cyc else "rgba(52, 211, 153, 0.12)"
            badge_border = "rgba(244, 63, 94, 0.3)" if has_cyc else "rgba(52, 211, 153, 0.3)"
            badge_color = "#FECDD3" if has_cyc else "#A7F3D0"

            mod_chips = "".join([f"<span class='code-chip {'cycle' if has_cyc else 'safe'}'>{m}</span>" for m in p_mods])
            scc_pills = ", ".join([f"SCC_{s}" for s in p_sccs])

            st.markdown(f"""
            <div class="pipeline-phase" style="border-left: 3px solid {'#F43F5E' if has_cyc else '#34D399'};">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.45rem;">
                        <span class="pipeline-phase-num">Phase {p_num:02d}</span>
                        <span style="font-size: 0.75rem; color: #64748B;">Components: {scc_pills}</span>
                        <span style="font-size: 0.7rem; font-weight: 600; color: {badge_color}; background: {badge_bg}; border: 1px solid {badge_border}; padding: 2px 7px; border-radius: 4px; margin-left: auto;">{badge_text}</span>
                    </div>
                    <div style="margin-bottom: 0.35rem;">
                        {mod_chips}
                    </div>
                    <div style="font-size: 0.8rem; color: #94A3B8;">
                        {expl}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if i < len(phases) - 1:
                st.markdown("<div class='pipeline-connector'>&darr;</div>", unsafe_allow_html=True)

    # ==========================================
    # TAB 2: Kahn's Stepper & Graph Animation
    # ==========================================
    with tab_stepper:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.5rem;'>Kahn's Algorithm In-Degree State Transition</div>", unsafe_allow_html=True)

        if kahn_steps:
            total_kahn = len(kahn_steps)
            kahn_key = "kahn_stepper_idx"
            if kahn_key not in st.session_state:
                st.session_state[kahn_key] = 0

            st.session_state[kahn_key] = max(0, min(st.session_state[kahn_key], total_kahn - 1))

            col_btn_prev, col_slide, col_btn_next = st.columns([1, 2, 1])
            with col_btn_prev:
                if st.button("&larr; Prev Step", key="btn_kahn_prev", disabled=(st.session_state[kahn_key] == 0), use_container_width=True):
                    st.session_state[kahn_key] -= 1
                    st.rerun()

            with col_slide:
                kahn_slider = st.slider(
                    "Kahn Step Slider",
                    0,
                    total_kahn - 1,
                    st.session_state[kahn_key],
                    format="Step %d",
                    label_visibility="collapsed"
                )
                if kahn_slider != st.session_state[kahn_key]:
                    st.session_state[kahn_key] = kahn_slider
                    st.rerun()

            with col_btn_next:
                if st.button("Next Step &rarr;", key="btn_kahn_next", disabled=(st.session_state[kahn_key] == total_kahn - 1), use_container_width=True):
                    st.session_state[kahn_key] += 1
                    st.rerun()

            step_idx = st.session_state[kahn_key]
            curr_step = kahn_steps[step_idx]
            deq_scc = curr_step.get("dequeued_scc")
            step_mods = curr_step.get("modules", [])
            queue_snap = curr_step.get("queue_snapshot", [])
            note = curr_step.get("note", "")

            # Active step visual card
            st.markdown(f"""
            <div style="background-color: #151F32; border: 1px solid #273449; border-radius: 8px; padding: 0.9rem 1.15rem; margin-top: 0.5rem; margin-bottom: 0.85rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: #FBBF24; text-transform: uppercase;">Step {curr_step.get('step')} of {total_kahn}: Dequeued SCC_{deq_scc}</span>
                    <span style="font-size: 0.75rem; color: #64748B;">In-Queue: {[f'SCC_{q}' for q in queue_snap]}</span>
                </div>
                <div style="font-size: 0.85rem; color: #F1F5F9; margin-bottom: 0.3rem;">
                    Modules: {', '.join([f'<code>{m}</code>' for m in step_mods])}
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8;">
                    {note}
                </div>
            </div>
            """, unsafe_allow_html=True)

            dot_step = generate_kahn_step_dot(data, step_idx)
            st.graphviz_chart(dot_step, use_container_width=True)

            # Compact step table
            with st.expander("Complete Kahn In-Degree Transition Table"):
                df_k = pd.DataFrame([{
                    "Step": s["step"],
                    "Component": f"SCC_{s['dequeued_scc']}",
                    "Modules": ", ".join(s["modules"]),
                    "Queue After Step": ", ".join([f"SCC_{q}" for q in s["queue_snapshot"]]),
                    "Transition": s["note"]
                } for s in kahn_steps])
                st.dataframe(df_k, use_container_width=True, hide_index=True)

    # Collapsible theory section
    with st.expander("Kahn's Algorithm Principles & Complexity"):
        st.markdown("""
        - **In-Degrees:** Each component tracks how many unresolved dependencies it is waiting for.
        - **Queue Mechanism:** Components with in-degree 0 are ready to execute and added to a FIFO queue.
        - **Transition:** As each component finishes, it decrements the in-degrees of its dependent neighbors.
        - **Complexity:** Time complexity is $\\mathcal{O}(V + E)$ and Space complexity is $\\mathcal{O}(V)$.
        """)
