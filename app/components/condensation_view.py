"""
Condensation DAG Component
Visualizes the Condensed Graph where each SCC is collapsed into a single component super-node.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from app.utils.graph_visualizer import generate_condensation_dot


def render_condensation_view(data: Dict[str, Any]):
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">DAG TRANSFORMATION</span>
        <h1 class="page-header-title">Condensation Directed Acyclic Graph</h1>
        <p class="page-header-desc">Contraction of cyclic Strongly Connected Components into composite super-nodes, producing a guaranteed acyclic graph.</p>
    </div>
    """, unsafe_allow_html=True)

    cond = data.get("condensation_dag", {})
    nodes = cond.get("nodes", [])
    edges = cond.get("edges", [])

    # Main Visual Element: Condensation Graph
    dot_cond = generate_condensation_dot(data)
    st.graphviz_chart(dot_cond, use_container_width=True)

    # Compact stats summary
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="padding: 0.8rem 1rem;">
            <div class="metric-label">Component Super-Nodes</div>
            <div class="metric-value" style="font-size: 1.5rem;">{len(nodes)}</div>
            <div class="metric-footer">Total SCC partitions in G</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="padding: 0.8rem 1rem;">
            <div class="metric-label">Cross-Component Dependencies</div>
            <div class="metric-value" style="font-size: 1.5rem;">{len(edges)}</div>
            <div class="metric-footer">Deduplicated inter-SCC edges</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Super-nodes Table
    st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.4rem;'>Component Super-Node Catalog</div>", unsafe_allow_html=True)
    if nodes:
        df_nodes = pd.DataFrame([{
            "Component ID": f"SCC_{n['id']}",
            "Classification": "Circular Group" if n.get("is_cycle") else "Acyclic",
            "Member Modules": ", ".join(n.get("modules", [])),
            "In-Degree": n.get("in_degree", 0),
            "Out-Degree": n.get("out_degree", 0)
        } for n in nodes])
        st.dataframe(df_nodes, use_container_width=True, hide_index=True)

    # Mathematical Proof
    with st.expander("Proof of Acyclicity in Condensation Graphs"):
        st.markdown("""
        **Theorem:** *For any directed graph $G$, the condensation graph $G^{SCC}$ is strictly a Directed Acyclic Graph (DAG).*
        
        **Proof by Contradiction:**
        1. Assume $G^{SCC}$ contains a directed cycle $C_1 \\to C_2 \\to \\dots \\to C_k \\to C_1$.
        2. By definition of condensation edges, an edge $C_i \\to C_{i+1}$ implies a path from some $u \\in C_i$ to $v \\in C_{i+1}$.
        3. Since each component $C_i$ is internally strongly connected, all vertices in $C_1 \\cup C_2 \\dots \\cup C_k$ are mutually reachable.
        4. This contradicts the maximality of Strongly Connected Components, which requires that all mutually reachable vertices belong to the same component.
        5. Therefore, $G^{SCC}$ contains no cycles. $\\blacksquare$
        """)
