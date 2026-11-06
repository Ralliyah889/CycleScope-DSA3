import pytest
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.cpp_runner import run_analyzer, ensure_binary_compiled
from app.utils.graph_visualizer import (
    generate_dependency_dot,
    generate_transposed_dot,
    generate_condensation_dot,
    get_module_scc_mapping
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


@pytest.fixture(scope="session", autouse=True)
def setup_binary():
    """Ensure C++ binary is compiled before tests run."""
    assert ensure_binary_compiled(), "C++ binary could not be compiled"


def test_sample_dependencies():
    """Test standard sample with cycle A-B-C and chain D through J."""
    sample_path = DATA_DIR / "sample_dependencies.csv"
    success, data, err = run_analyzer(str(sample_path))

    assert success, f"Analyzer failed: {err}"
    assert data["status"] == "success"
    assert data["stats"]["total_modules"] == 10
    assert data["stats"]["total_dependencies"] == 10
    assert data["stats"]["has_cycles"] is True
    assert data["stats"]["cycle_groups_count"] == 1
    assert data["stats"]["independent_modules_count"] == 7

    # Check cycle group contains A, B, C
    sccs = data["kosaraju_stages"]["stage3_sccs"]
    cycle_scc = next(s for s in sccs if s["is_cycle"])
    assert set(cycle_scc["modules"]) == {"A", "B", "C"}

    # Check topological order validity
    topo = data["topological_sort"]
    assert topo["is_dag"] is True
    assert len(topo["component_order"]) == len(sccs)


def test_no_cycles():
    """Test clean microservice architecture with no circular dependencies."""
    sample_path = DATA_DIR / "no_cycles.csv"
    success, data, err = run_analyzer(str(sample_path))

    assert success, f"Analyzer failed: {err}"
    assert data["stats"]["has_cycles"] is False
    assert data["stats"]["cycle_groups_count"] == 0
    assert data["stats"]["total_modules"] == 9
    assert data["topological_sort"]["is_dag"] is True


def test_multiple_cycles():
    """Test graph containing 2 distinct circular dependency groups."""
    sample_path = DATA_DIR / "multiple_cycles.csv"
    success, data, err = run_analyzer(str(sample_path))

    assert success, f"Analyzer failed: {err}"
    assert data["stats"]["has_cycles"] is True
    assert data["stats"]["cycle_groups_count"] == 2
    assert data["stats"]["independent_modules_count"] == 3


def test_self_loop():
    """Test graph with self-loop dependency (Module depending on itself)."""
    sample_path = DATA_DIR / "self_loop.csv"
    success, data, err = run_analyzer(str(sample_path))

    assert success, f"Analyzer failed: {err}"
    assert data["stats"]["has_cycles"] is True
    assert data["stats"]["cycle_groups_count"] == 1

    sccs = data["kosaraju_stages"]["stage3_sccs"]
    self_loop_scc = next(s for s in sccs if s["cycle_type"] == "SELF_LOOP")
    assert self_loop_scc["modules"] == ["RecursiveCompiler"]


def test_disconnected_graph():
    """Test graph with disconnected clusters and isolated modules."""
    sample_path = DATA_DIR / "disconnected.csv"
    success, data, err = run_analyzer(str(sample_path))

    assert success, f"Analyzer failed: {err}"
    assert data["stats"]["total_modules"] == 7
    assert data["stats"]["cycle_groups_count"] == 1
    assert data["topological_sort"]["is_dag"] is True


def test_empty_or_invalid():
    """Test invalid / empty input handling."""
    sample_path = DATA_DIR / "empty_invalid.csv"
    success, data, err = run_analyzer(str(sample_path))

    assert not success
    assert "File contained no valid module records" in err


def test_raw_csv_content():
    """Test direct string CSV input via tempfile pipeline."""
    csv_text = "Module,Depends_On\nX,Y\nY,Z\nZ,X\n"
    success, data, err = run_analyzer(csv_text, is_content=True)

    assert success, f"Failed on raw CSV: {err}"
    assert data["stats"]["total_modules"] == 3
    assert data["stats"]["has_cycles"] is True
    assert data["stats"]["cycle_groups_count"] == 1


def test_graph_visualizer_dot_generation():
    """Test Graphviz DOT string generators."""
    csv_text = "Module,Depends_On\nA,B\nB,C\nC,A\nD,C\n"
    success, data, err = run_analyzer(csv_text, is_content=True)
    assert success

    dep_dot = generate_dependency_dot(data, highlight_cycles=True)
    assert "digraph DependencyGraph" in dep_dot
    assert '"A"' in dep_dot
    assert '"B" -> "A"' in dep_dot

    trans_dot = generate_transposed_dot(data)
    assert "digraph TransposedGraph" in trans_dot
    assert '"A" -> "B"' in trans_dot

    cond_dot = generate_condensation_dot(data)
    assert "digraph CondensationDAG" in cond_dot
    assert "SCC_" in cond_dot

    mapping = get_module_scc_mapping(data)
    assert "A" in mapping
    assert mapping["A"]["is_cycle"] is True
