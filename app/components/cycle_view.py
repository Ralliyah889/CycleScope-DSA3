"""
Circular Dependency Analysis Component
Detailed breakdown of cycles into compact cards, separate self-loop analysis,
and architectural remediation strategies.
"""

import streamlit as st
from typing import Dict, Any


def render_cycle_view(data: Dict[str, Any]):
    st.markdown("""
    <div class="page-header-container">
        <span class="page-badge">CYCLE ISOLATION</span>
        <h1 class="page-header-title">Circular Dependency Analysis</h1>
        <p class="page-header-desc">Detailed breakdown of mutual dependency cycles, self-loop recursions, and decoupling strategies.</p>
    </div>
    """, unsafe_allow_html=True)

    stats = data.get("stats", {})
    has_cycles = stats.get("has_cycles", False)
    cycle_count = stats.get("cycle_groups_count", 0)
    sccs = data.get("kosaraju_stages", {}).get("stage3_sccs", [])

    mutual_cycles = [s for s in sccs if s.get("is_cycle") and s.get("cycle_type") == "MUTUAL_CYCLE"]
    self_loops = [s for s in sccs if s.get("is_cycle") and s.get("cycle_type") == "SELF_LOOP"]
    acyclic_sccs = [s for s in sccs if not s.get("is_cycle")]

    if not has_cycles:
        st.markdown("""
        <div class="status-indicator status-indicator-success">
            <div class="status-indicator-dot"></div>
            <div>
                <strong>Acyclic Graph &middot; 0 Circular Dependencies</strong><br/>
                <span style="font-size: 0.82rem; color: #6EE7B7;">No circular dependency groups detected. All software modules follow a strict hierarchical build path.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-indicator status-indicator-danger">
            <div class="status-indicator-dot"></div>
            <div>
                <strong>{cycle_count} Circular Dependency Group{'s' if cycle_count != 1 else ''} Identified</strong><br/>
                <span style="font-size: 0.82rem; color: #FDA4AF;">These module groups contain closed loops preventing direct linear compilation.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 1. Mutual Dependency Cycles
    if mutual_cycles:
        st.markdown(f"<div style='font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin: 1rem 0 0.5rem 0;'>Mutual Dependency Groups ({len(mutual_cycles)})</div>", unsafe_allow_html=True)
        
        for idx, cs in enumerate(mutual_cycles):
            scc_id = cs.get("id")
            mods = cs.get("modules", [])
            chips = "".join([f"<span class='code-chip cycle'>{m}</span>" for m in mods])

            st.markdown(f"""
            <div style="background-color: #151F32; border: 1px solid #273449; border-left: 3px solid #F43F5E; border-radius: 6px; padding: 0.9rem 1.15rem; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.45rem;">
                    <div>
                        <span style="font-weight: 700; font-size: 0.9rem; color: #F1F5F9; margin-right: 0.6rem;">Cycle Group #{idx + 1}</span>
                        <span style="font-size: 0.75rem; color: #64748B;">SCC_{scc_id} &middot; {len(mods)} Modules</span>
                    </div>
                    <span style="font-size: 0.72rem; font-weight: 600; color: #FECDD3; background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.35); padding: 2px 7px; border-radius: 4px;">MUTUAL CYCLE</span>
                </div>
                <div style="margin-bottom: 0.4rem;">
                    {chips}
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4;">
                    Mutual Reachability: Every module in this group directly or indirectly depends on all other members (&forall; u, v: u &rightsquigarrow; v and v &rightsquigarrow; u).
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. Self-Loop Dependencies
    if self_loops:
        st.markdown(f"<div style='font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin: 1rem 0 0.5rem 0;'>Self-Loop Dependencies ({len(self_loops)})</div>", unsafe_allow_html=True)
        
        for idx, sl in enumerate(self_loops):
            scc_id = sl.get("id")
            mods = sl.get("modules", [])
            mod_name = mods[0] if mods else "Unknown"

            st.markdown(f"""
            <div style="background-color: #151F32; border: 1px solid #273449; border-left: 3px solid #FBBF24; border-radius: 6px; padding: 0.9rem 1.15rem; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.45rem;">
                    <div>
                        <span style="font-weight: 700; font-size: 0.9rem; color: #F1F5F9; margin-right: 0.6rem;">Self-Loop #{idx + 1}</span>
                        <span style="font-size: 0.75rem; color: #64748B;">SCC_{scc_id} &middot; 1 Module</span>
                    </div>
                    <span style="font-size: 0.72rem; font-weight: 600; color: #FEF08A; background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.35); padding: 2px 7px; border-radius: 4px;">SELF-LOOP</span>
                </div>
                <div style="margin-bottom: 0.3rem;">
                    <span class='code-chip' style='border-color: rgba(251, 191, 36, 0.4); color: #FEF08A;'>{mod_name} &rarr; {mod_name}</span>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8;">
                    Module <code>{mod_name}</code> directly requires itself, creating an immediate single-node recursion.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. Acyclic / Normal Components
    st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F1F5F9; margin: 1rem 0 0.5rem 0;'>Normal / Acyclic Modules</div>", unsafe_allow_html=True)
    if acyclic_sccs:
        acyclic_mods = [m for s in acyclic_sccs for m in s.get("modules", [])]
        chips = "".join([f"<span class='code-chip safe'>{m}</span>" for m in acyclic_mods])
        st.markdown(f"""
        <div style="background-color: #151F32; border: 1px solid #273449; border-radius: 6px; padding: 0.85rem 1rem;">
            <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.4rem;">{len(acyclic_mods)} modules are cycle-free and satisfy DAG constraints:</div>
            {chips}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("All modules in this dataset participate in circular dependency groups.")

    # Refactoring Patterns
    with st.expander("Architectural Decoupling Patterns"):
        st.markdown("""
        - **Dependency Inversion (DIP):** Introduce an abstract interface $I$ between Module $A$ and Module $B$.
        - **Extract Common Library:** Separate shared utilities or data structures into a low-level `Types` or `Common` module.
        - **Event-Driven Messaging:** Decouple synchronous calls using an event emitter or message queue.
        """)
