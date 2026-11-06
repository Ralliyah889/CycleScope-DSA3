"""
Dependency Graph Component
Interactive visualization of the full module dependency graph with cycle coloring.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from app.utils.graph_visualizer import generate_dependency_dot, get_module_scc_mapping


def render_graph_view(data: Dict[str, Any]):
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">GRAPH TOPOLOGY</span>
        <h1 class="page-header-title">Module Dependency Graph</h1>
        <p class="page-header-desc">Full topological view of directed build dependencies. Circular dependency groups are isolated in distinct hues.</p>
    </div>
    """, unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    with col_ctrl1:
        highlight_cycles = st.toggle("Highlight Cycle Groups", value=True)
    with col_ctrl2:
        show_details_table = st.toggle("Show Dependency Table", value=False)

    # Render Graph
    dot_str = generate_dependency_dot(data, highlight_cycles=highlight_cycles)
    st.graphviz_chart(dot_str, use_container_width=True)

    # Compact Developer Legend
    st.markdown("""
    <div style="background-color: #151F32; border: 1px solid #273449; border-radius: 6px; padding: 0.6rem 0.9rem; margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 1.25rem; font-size: 0.8rem; color: #94A3B8;">
        <div><span style="display:inline-block; width:10px; height:10px; background:#151F32; border:1px solid #273449; border-radius:2px; margin-right:5px;"></span> <span style="color:#F1F5F9;">Slate:</span> Acyclic / Independent</div>
        <div><span style="display:inline-block; width:10px; height:10px; background:#2D1522; border:1px solid #F43F5E; border-radius:2px; margin-right:5px;"></span> <span style="color:#FECDD3;">Tinted:</span> Circular Dependency Component (SCC)</div>
        <div><span style="color:#6C8CFF; font-weight:600;">&rarr;</span> <span style="color:#F1F5F9;">Arrow:</span> B &rarr; A (B must be built before A)</div>
    </div>
    """, unsafe_allow_html=True)

    # Dependency table
    if show_details_table:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        edges = data.get("edges", [])
        if edges:
            df_edges = pd.DataFrame(edges)
            df_edges.columns = ["Prerequisite (From)", "Dependent Module (To)", "Semantics"]
            st.dataframe(df_edges, use_container_width=True, hide_index=True)
        else:
            st.info("No inter-module dependencies present in current dataset.")

    # Module inspector
    with st.expander("Module Property Inspector"):
        mod_map = get_module_scc_mapping(data)
        vertices = data.get("vertices", [])
        if vertices:
            selected_mod = st.selectbox("Select Module to Inspect:", vertices, label_visibility="collapsed")
            info = mod_map.get(selected_mod, {})
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.caption("Module")
                st.code(selected_mod)
            with c2:
                st.caption("Component ID")
                st.code(f"SCC_{info.get('scc_id', 'N/A')}")
            with c3:
                st.caption("Cycle Classification")
                is_cyc = info.get("is_cycle", False)
                ctype = info.get("cycle_type", "ACYCLIC")
                badge_style = "color: #F43F5E; font-weight: 600;" if is_cyc else "color: #34D399; font-weight: 600;"
                st.markdown(f"<span style='{badge_style}'>{ctype}</span>", unsafe_allow_html=True)
            with c4:
                st.caption("Cluster Size")
                st.markdown(f"**{info.get('scc_size', 1)}** module(s)")
