"""
Overview Dashboard Component
Displays compact KPI metric cards, clear analysis status indicator, and graph architecture preview.
"""

import streamlit as st
from typing import Dict, Any
from app.utils.graph_visualizer import generate_dependency_dot


def render_overview(data: Dict[str, Any]):
    # Page Header
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">DASHBOARD</span>
        <h1 class="page-header-title">System Overview</h1>
        <p class="page-header-desc">High-level topology metrics, circular dependency status, and module architecture.</p>
    </div>
    """, unsafe_allow_html=True)

    stats = data.get("stats", {})
    total_mods = stats.get("total_modules", 0)
    total_deps = stats.get("total_dependencies", 0)
    cycle_groups = stats.get("cycle_groups_count", 0)
    has_cycles = stats.get("has_cycles", False)
    phases = data.get("topological_sort", {}).get("phases", [])
    num_phases = len(phases)

    # Analysis Status Indicator
    if has_cycles:
        st.markdown(f"""
        <div class="status-indicator status-indicator-danger">
            <div class="status-indicator-dot"></div>
            <div>
                <strong>Analysis Status: Circular Dependencies Detected ({cycle_groups} Group{'s' if cycle_groups != 1 else ''})</strong><br/>
                <span style="font-size: 0.82rem; color: #FDA4AF;">Kosaraju's algorithm identified closed dependency cycles. Mutual dependencies prevent linear execution.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-indicator status-indicator-success">
            <div class="status-indicator-dot"></div>
            <div>
                <strong>Analysis Status: Clean DAG &middot; No Circular Dependencies</strong><br/>
                <span style="font-size: 0.82rem; color: #6EE7B7;">The dependency graph is strictly acyclic. Modules can be built linearly or in parallel without deadlocks.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Four Compact Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Modules</div>
            <div class="metric-value">{total_mods}</div>
            <div class="metric-footer">Vertices in dependency graph</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Dependencies</div>
            <div class="metric-value">{total_deps}</div>
            <div class="metric-footer">Directed prerequisite edges</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        footer_cls = "danger" if cycle_groups > 0 else "success"
        footer_text = f"{cycle_groups} Mutual Loop{'s' if cycle_groups != 1 else ''}" if cycle_groups > 0 else "0 Cycles (Clean)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Circular Groups</div>
            <div class="metric-value">{cycle_groups}</div>
            <div class="metric-footer {footer_cls}">{footer_text}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Execution Phases</div>
            <div class="metric-value">{num_phases}</div>
            <div class="metric-footer accent">Kahn Topological Depth</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Graph Overview
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
        <span style="font-weight: 600; font-size: 0.95rem; color: #F1F5F9;">Dependency Architecture Overview</span>
        <span style="font-size: 0.8rem; color: #64748B;">Edge convention: <code>B &rarr; A</code> (B is required before A)</span>
    </div>
    """, unsafe_allow_html=True)

    dot_str = generate_dependency_dot(data, highlight_cycles=True)
    st.graphviz_chart(dot_str, use_container_width=True)

    # Collapsible Architecture Context
    with st.expander("Topology Conventions & Definitions"):
        st.markdown("""
        - **Vertices ($V$):** Software modules or compilation packages.
        - **Directed Edges ($E$):** Dependency flow. If Module $A$ depends on $B$, an edge $B \\to A$ ensures $B$ compiles before $A$.
        - **Strongly Connected Components (SCCs):** Subgraphs where every vertex is mutually reachable from every other vertex.
        - **Condensation DAG:** A contracted acyclic graph where each cyclic SCC is treated as a single composite node.
        """)
