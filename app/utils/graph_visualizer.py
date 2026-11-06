"""
Graph Visualization Utility
Generates Graphviz DOT strings with a modern dark developer tool aesthetic.
Uses the project palette:
- Background: transparent
- Cards: #151F32, Borders: #273449
- Accents: #6C8CFF, #A78BFA, #34D399, #FBBF24, #F43F5E
"""

from typing import Dict, Any, List

# Distinct, accessible dark-theme color palettes for highlighting SCCs and cycles
DARK_CYCLE_PALETTES = [
    {"fill": "#2D1522", "border": "#F43F5E", "text": "#FECDD3", "edge": "#F43F5E"},  # Rose / Crimson
    {"fill": "#2D1C12", "border": "#FB923C", "text": "#FED7AA", "edge": "#FB923C"},  # Amber / Orange
    {"fill": "#251833", "border": "#A78BFA", "text": "#DDD6FE", "edge": "#A78BFA"},  # Purple / Violet
    {"fill": "#112727", "border": "#2DD4BF", "text": "#99F6E4", "edge": "#2DD4BF"},  # Emerald / Teal
    {"fill": "#2B2310", "border": "#FBBF24", "text": "#FEF08A", "edge": "#FBBF24"},  # Yellow / Gold
    {"fill": "#172338", "border": "#60A5FA", "text": "#BFDBFE", "edge": "#60A5FA"},  # Blue
]

ACYCLIC_FILL = "#151F32"
ACYCLIC_BORDER = "#273449"
ACYCLIC_TEXT = "#F1F5F9"
NORMAL_EDGE = "#475569"


def get_module_scc_mapping(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Maps each module name to its SCC metadata."""
    mapping = {}
    sccs = data.get("kosaraju_stages", {}).get("stage3_sccs", [])
    cycle_idx = 0
    for scc in sccs:
        is_cycle = scc.get("is_cycle", False)
        scc_id = scc.get("id", 0)
        cycle_type = scc.get("cycle_type", "ACYCLIC")

        if is_cycle:
            palette = DARK_CYCLE_PALETTES[cycle_idx % len(DARK_CYCLE_PALETTES)]
            color = palette["fill"]
            border = palette["border"]
            font_color = palette["text"]
            edge_color = palette["edge"]
            cycle_idx += 1
        else:
            color = ACYCLIC_FILL
            border = ACYCLIC_BORDER
            font_color = ACYCLIC_TEXT
            edge_color = NORMAL_EDGE

        for mod in scc.get("modules", []):
            mapping[mod] = {
                "scc_id": scc_id,
                "is_cycle": is_cycle,
                "cycle_type": cycle_type,
                "color": color,
                "border": border,
                "font_color": font_color,
                "edge_color": edge_color,
                "scc_size": len(scc.get("modules", []))
            }
    return mapping


def generate_dependency_dot(data: Dict[str, Any], highlight_cycles: bool = True) -> str:
    """
    Constructs Graphviz DOT representation of the module dependency graph.
    Edge convention: B -> A (B must be built before A / A depends on B).
    """
    vertices = data.get("vertices", [])
    edges = data.get("edges", [])
    mod_map = get_module_scc_mapping(data)

    dot = [
        'digraph DependencyGraph {',
        '  graph [rankdir=LR, bgcolor="transparent", nodesep=0.45, ranksep=0.65];',
        '  node [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=10.5, shape=box, style="filled,rounded", penwidth=1.5, margin="0.16,0.1"];',
        '  edge [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=8.5, color="#475569", arrowsize=0.7, penwidth=1.3];',
        ''
    ]

    # Add Nodes
    for v in vertices:
        info = mod_map.get(v, {"is_cycle": False, "color": ACYCLIC_FILL, "border": ACYCLIC_BORDER, "font_color": ACYCLIC_TEXT, "scc_id": 0})
        if highlight_cycles and info["is_cycle"]:
            fill = info["color"]
            border = info["border"]
            font_color = info.get("font_color", "#F1F5F9")
            tooltip = f"Module: {v} (Circular SCC {info['scc_id']})"
            label = f"{v}\\n[SCC {info['scc_id']} ↻]"
        else:
            fill = ACYCLIC_FILL
            border = ACYCLIC_BORDER
            font_color = ACYCLIC_TEXT
            tooltip = f"Module: {v} (Independent)"
            label = v

        dot.append(f'  "{v}" [label="{label}", fillcolor="{fill}", color="{border}", fontcolor="{font_color}", tooltip="{tooltip}"];')

    dot.append('')

    # Add Edges: from B to A (B must be processed before A)
    for edge in edges:
        u = edge.get("from")
        v = edge.get("to")
        u_info = mod_map.get(u, {})
        v_info = mod_map.get(v, {})
        in_same_cycle = (
            highlight_cycles and 
            u_info.get("is_cycle", False) and 
            v_info.get("is_cycle", False) and 
            u_info.get("scc_id") == v_info.get("scc_id")
        )

        if in_same_cycle:
            edge_col = u_info.get("edge_color", "#F43F5E")
            dot.append(f'  "{u}" -> "{v}" [color="{edge_col}", penwidth=2.0, tooltip="{v} depends on {u} (Cycle)"];')
        else:
            dot.append(f'  "{u}" -> "{v}" [tooltip="{v} depends on {u}"];')

    dot.append('}')
    return '\n'.join(dot)


def generate_transposed_dot(data: Dict[str, Any]) -> str:
    """
    Constructs Graphviz DOT for the Transposed Graph (G^T) used in Kosaraju Step 2.
    All edges are reversed.
    """
    vertices = data.get("vertices", [])
    transposed_edges = data.get("kosaraju_stages", {}).get("stage2_transposed_edges", [])

    dot = [
        'digraph TransposedGraph {',
        '  graph [rankdir=LR, bgcolor="transparent", nodesep=0.45, ranksep=0.65];',
        '  node [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=10.5, shape=box, style="filled,rounded", fillcolor="#161B2E", color="#6C8CFF", fontcolor="#E2E8F0", penwidth=1.5, margin="0.16,0.1"];',
        '  edge [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=8.5, color="#A78BFA", arrowsize=0.7, penwidth=1.3, style="dashed"];',
        ''
    ]

    for v in vertices:
        dot.append(f'  "{v}" [label="{v}"];')

    dot.append('')
    for edge in transposed_edges:
        u = edge.get("from")
        v = edge.get("to")
        dot.append(f'  "{u}" -> "{v}" [label="rev", tooltip="Reversed: {u} -> {v}"];')

    dot.append('}')
    return '\n'.join(dot)


def generate_condensation_dot(data: Dict[str, Any]) -> str:
    """
    Constructs Graphviz DOT for the Condensation DAG.
    Each SCC is rendered as a component super-node.
    """
    cond = data.get("condensation_dag", {})
    nodes = cond.get("nodes", [])
    edges = cond.get("edges", [])

    dot = [
        'digraph CondensationDAG {',
        '  graph [rankdir=LR, bgcolor="transparent", nodesep=0.55, ranksep=0.75];',
        '  node [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=10.5, shape=box, style="filled,rounded", penwidth=1.6, margin="0.18,0.12"];',
        '  edge [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=8.5, color="#6C8CFF", arrowsize=0.75, penwidth=1.8];',
        ''
    ]

    for node in nodes:
        scc_id = node.get("id")
        modules = node.get("modules", [])
        is_cycle = node.get("is_cycle", False)
        mods_str = ", ".join(modules)

        if is_cycle:
            fill = "#2D1522"
            border = "#F43F5E"
            font_color = "#FECDD3"
            badge = "CYCLE"
        else:
            fill = "#0E241D"
            border = "#34D399"
            font_color = "#A7F3D0"
            badge = "DAG SAFE"

        label = f"SCC_{scc_id} [{badge}]\\n{{{mods_str}}}"
        dot.append(f'  "scc_{scc_id}" [label="{label}", fillcolor="{fill}", color="{border}", fontcolor="{font_color}"];')

    dot.append('')
    for edge in edges:
        u = edge.get("from")
        v = edge.get("to")
        dot.append(f'  "scc_{u}" -> "scc_{v}" [tooltip="SCC_{u} -> SCC_{v}"];')

    dot.append('}')
    return '\n'.join(dot)


def generate_kahn_step_dot(data: Dict[str, Any], current_step_idx: int) -> str:
    """
    Constructs Graphviz DOT showing the Condensation DAG highlighted
    at a specific step of Kahn's Algorithm.
    """
    cond = data.get("condensation_dag", {})
    nodes = cond.get("nodes", [])
    edges = cond.get("edges", [])
    topo = data.get("topological_sort", {})
    kahn_steps = topo.get("kahn_steps", [])

    if not kahn_steps or current_step_idx < 0:
        return generate_condensation_dot(data)

    step_idx = min(current_step_idx, len(kahn_steps) - 1)
    step = kahn_steps[step_idx]
    active_scc = step.get("dequeued_scc")
    queue_sccs = step.get("queue_snapshot", [])

    processed_sccs = [kahn_steps[i].get("dequeued_scc") for i in range(step_idx)]

    dot = [
        'digraph KahnDAG {',
        '  graph [rankdir=LR, bgcolor="transparent", nodesep=0.55, ranksep=0.75];',
        '  node [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=10.5, shape=box, style="filled,rounded", penwidth=1.6, margin="0.18,0.12"];',
        '  edge [fontname="SF Pro Display, -apple-system, Inter, sans-serif", fontsize=8.5, color="#334155", arrowsize=0.7, penwidth=1.3];',
        ''
    ]

    for node in nodes:
        scc_id = node.get("id")
        modules = node.get("modules", [])
        mods_str = ", ".join(modules)

        if scc_id == active_scc:
            fill = "#2B2310"
            border = "#FBBF24"
            font_color = "#FEF08A"
            status = "EXECUTING"
            penwidth = 2.4
        elif scc_id in queue_sccs:
            fill = "#172554"
            border = "#6C8CFF"
            font_color = "#BFDBFE"
            status = "QUEUED"
            penwidth = 1.8
        elif scc_id in processed_sccs:
            fill = "#0B1020"
            border = "#273449"
            font_color = "#64748B"
            status = "RESOLVED"
            penwidth = 1.2
        else:
            fill = "#151F32"
            border = "#1E293B"
            font_color = "#94A3B8"
            status = "PENDING"
            penwidth = 1.2

        label = f"SCC_{scc_id} [{status}]\\n{{{mods_str}}}"
        dot.append(f'  "scc_{scc_id}" [label="{label}", fillcolor="{fill}", color="{border}", fontcolor="{font_color}", penwidth={penwidth}];')

    dot.append('')
    for edge in edges:
        u = edge.get("from")
        v = edge.get("to")
        if u == active_scc:
            dot.append(f'  "scc_{u}" -> "scc_{v}" [color="#FBBF24", penwidth=2.2];')
        elif u in processed_sccs:
            dot.append(f'  "scc_{u}" -> "scc_{v}" [color="#273449", penwidth=1.0];')
        else:
            dot.append(f'  "scc_{u}" -> "scc_{v}" [color="#475569", penwidth=1.3];')

    dot.append('}')
    return '\n'.join(dot)
