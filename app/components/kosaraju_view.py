"""
Kosaraju Algorithm Visualization Component
Visualizes the 3 core stages of Kosaraju's SCC algorithm with horizontal stepper
and interactive previous/next step-by-step walkthrough.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from app.utils.graph_visualizer import generate_transposed_dot


def render_kosaraju_view(data: Dict[str, Any]):
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">ALGORITHM ENGINE</span>
        <h1 class="page-header-title">Kosaraju SCC Algorithm</h1>
        <p class="page-header-desc">Three-stage linear time &Omicron;(V + E) discovery of Strongly Connected Components using DFS and graph transposition.</p>
    </div>
    """, unsafe_allow_html=True)

    kosaraju = data.get("kosaraju_stages", {})
    finishing_order = kosaraju.get("stage1_finishing_order", [])
    stage1_trace = kosaraju.get("stage1_trace", [])
    transposed_edges = kosaraju.get("stage2_transposed_edges", [])
    sccs = kosaraju.get("stage3_sccs", [])
    stage3_trace = kosaraju.get("stage3_trace", [])

    # Horizontal Stages Stepper
    stage_choice = st.radio(
        "Algorithm Stages:",
        [
            "1. First DFS & Finishing Order",
            "2. Transpose Graph (Gᵀ)",
            "3. Second DFS & SCCs",
            "4. Step-by-Step Interactive Stepper"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # ==========================================
    # STAGE 1: First DFS
    # ==========================================
    if stage_choice.startswith("1."):
        st.markdown("""
        <div class="dev-card">
            <div class="dev-card-title">Stage 1: Post-Order DFS Exploration on Original Graph G</div>
            <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;">
                A standard DFS is executed on G. When a vertex finishes visiting all outgoing neighbors, it is pushed onto an execution stack.
                The vertex at the stack top belongs to a <strong>source component</strong> in the condensation DAG.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_st1_left, col_st1_right = st.columns([1, 1])
        with col_st1_left:
            st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.4rem;'>Finishing Stack (Top &rarr; Bottom)</div>", unsafe_allow_html=True)
            stack_reversed = list(reversed(finishing_order))
            if stack_reversed:
                df_stack = pd.DataFrame({
                    "Index": [f"Top" if i == 0 else f"+{i}" for i in range(len(stack_reversed))],
                    "Module Name": stack_reversed
                })
                st.dataframe(df_stack, use_container_width=True, hide_index=True)
            else:
                st.info("No vertices processed.")

        with col_st1_right:
            st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.4rem;'>Finishing Sequence (Chronological)</div>", unsafe_allow_html=True)
            if finishing_order:
                chips_html = "".join([f"<span class='code-chip'>{idx+1}. {name}</span>" for idx, name in enumerate(finishing_order)])
                st.markdown(f"<div style='background:#151F32; border:1px solid #273449; border-radius:6px; padding:0.75rem;'>{chips_html}</div>", unsafe_allow_html=True)

        with st.expander("Detailed DFS-1 Step Trace Log"):
            if stage1_trace:
                df_trace = pd.DataFrame(stage1_trace)
                st.dataframe(df_trace[["action", "vertex", "target", "note"]], use_container_width=True, hide_index=True)

    # ==========================================
    # STAGE 2: Transpose Graph
    # ==========================================
    elif stage_choice.startswith("2."):
        st.markdown("""
        <div class="dev-card">
            <div class="dev-card-title">Stage 2: Transpose Graph Construction (Gᵀ)</div>
            <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;">
                Every directed edge <code>u &rarr; v</code> in G is reversed to <code>v &rarr; u</code> in G<sup>T</sup>.
                Mutual reachability within an SCC is preserved, but cross-component paths are reversed, preventing DFS leaks.
            </p>
        </div>
        """, unsafe_allow_html=True)

        dot_transposed = generate_transposed_dot(data)
        st.graphviz_chart(dot_transposed, use_container_width=True)

        st.caption(f"Reversed edges count: <code>{len(transposed_edges)}</code>. Dashed edges show inverted dependency paths.")

    # ==========================================
    # STAGE 3: Second DFS
    # ==========================================
    elif stage_choice.startswith("3."):
        st.markdown("""
        <div class="dev-card">
            <div class="dev-card-title">Stage 3: Second DFS on Transposed Graph Gᵀ</div>
            <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;">
                Vertices are popped from the stack in decreasing order of finishing times.
                DFS is executed on unvisited vertices in G<sup>T</sup>. Each connected traversal defines one Strongly Connected Component.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div style='font-size: 0.9rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.6rem;'>Discovered Components ({len(sccs)})</div>", unsafe_allow_html=True)

        for scc in sccs:
            scc_id = scc.get("id")
            mods = scc.get("modules", [])
            is_cycle = scc.get("is_cycle", False)
            cycle_type = scc.get("cycle_type", "ACYCLIC")

            badge_border = "#F43F5E" if is_cycle else "#34D399"
            badge_color = "#FECDD3" if is_cycle else "#A7F3D0"
            status_text = f"CIRCULAR ({cycle_type})" if is_cycle else "INDEPENDENT"

            mod_chips = "".join([f"<span class='code-chip {'cycle' if is_cycle else 'safe'}'>{m}</span>" for m in mods])

            st.markdown(f"""
            <div style="background-color: #151F32; border: 1px solid #273449; border-left: 3px solid {badge_border}; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: 600; font-size: 0.88rem; color: #F1F5F9; margin-right: 0.75rem;">SCC_{scc_id}</span>
                    {mod_chips}
                </div>
                <span style="font-size: 0.75rem; font-weight: 600; color: {badge_color};">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("Detailed DFS-2 Step Trace Log"):
            if stage3_trace:
                df_t3 = pd.DataFrame(stage3_trace)
                st.dataframe(df_t3, use_container_width=True, hide_index=True)

    # ==========================================
    # STAGE 4: Interactive Stepper with Prev/Next
    # ==========================================
    elif stage_choice.startswith("4."):
        st.markdown("""
        <div class="dev-card">
            <div class="dev-card-title">Step-by-Step Algorithm Execution Trace</div>
            <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;">
                Step through internal operations of First DFS and Second DFS with precise stack and traversal logging.
            </p>
        </div>
        """, unsafe_allow_html=True)

        sub_mode = st.radio(
            "Select Sub-Stage:",
            ["Stage 1: First DFS Exploration", "Stage 3: Second DFS SCC Discovery"],
            horizontal=True
        )

        trace = stage1_trace if sub_mode.startswith("Stage 1") else stage3_trace

        if not trace:
            st.info("No trace steps available for this stage.")
            return

        total_steps = len(trace)

        # Initialize session state for step index if needed
        state_key = "kosaraju_stepper_idx"
        if state_key not in st.session_state:
            st.session_state[state_key] = 0

        # Clamp
        st.session_state[state_key] = max(0, min(st.session_state[state_key], total_steps - 1))

        # Prev / Next Controls
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 2, 1])

        with col_ctrl1:
            if st.button("&larr; Previous", key="btn_prev_step", disabled=(st.session_state[state_key] == 0), use_container_width=True):
                st.session_state[state_key] -= 1
                st.rerun()

        with col_ctrl2:
            slider_val = st.slider(
                "Step Position",
                0,
                total_steps - 1,
                st.session_state[state_key],
                format="Step %d",
                label_visibility="collapsed"
            )
            if slider_val != st.session_state[state_key]:
                st.session_state[state_key] = slider_val
                st.rerun()

        with col_ctrl3:
            if st.button("Next &rarr;", key="btn_next_step", disabled=(st.session_state[state_key] == total_steps - 1), use_container_width=True):
                st.session_state[state_key] += 1
                st.rerun()

        curr_idx = st.session_state[state_key]
        curr = trace[curr_idx]

        # Step Detail Card
        st.markdown(f"""
        <div style="background-color: #151F32; border: 1px solid #273449; border-radius: 8px; padding: 1rem 1.25rem; margin-top: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <span style="font-size: 0.78rem; font-weight: 700; color: #6C8CFF; text-transform: uppercase;">Step {curr_idx + 1} of {total_steps}</span>
                <span class="code-chip">{curr.get('action')}</span>
            </div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.4rem;">
                Active Vertex: <span style="color: #6C8CFF;">{curr.get('vertex')}</span>
                {f" &rarr; Target: <span style='color: #A78BFA;'>{curr.get('target')}</span>" if curr.get('target') else ''}
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.35rem; line-height: 1.4;">
                {curr.get('note')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if curr.get("stack_snapshot"):
            st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
            stack_chips = "".join([f"<span class='code-chip'>{s}</span>" for s in curr.get("stack_snapshot", [])])
            st.markdown(f"<span style='font-size: 0.8rem; color: #64748B; margin-right: 0.5rem;'>Stack (Bottom &rarr; Top):</span> {stack_chips}", unsafe_allow_html=True)
