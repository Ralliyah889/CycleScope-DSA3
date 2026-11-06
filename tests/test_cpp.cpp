#include "graph.h"
#include "kosaraju.h"
#include "condensation.h"
#include "topological_sort.h"
#include <iostream>
#include <cassert>
#include <algorithm>
#include <set>

void test_linear_dag() {
    std::cout << "[TEST] Running Linear DAG test..." << std::endl;
    Graph g;
    // B -> A (A depends on B), C -> B (B depends on C)
    // Execution order should be: C, then B, then A
    g.add_dependency("A", "B");
    g.add_dependency("B", "C");

    assert(g.get_num_vertices() == 3);
    assert(g.get_num_edges() == 2);

    KosarajuAlgorithm kosaraju(g);
    KosarajuResult res = kosaraju.run();

    assert(res.total_sccs == 3);
    assert(res.cycle_count == 0);
    assert(!res.has_cycles);

    CondensationGraph cond(g, res.sccs);
    assert(cond.get_num_components() == 3);

    KahnTopologicalSort kahn(cond);
    TopologicalSortResult topo = kahn.run();
    assert(topo.is_dag);
    assert(topo.component_order.size() == 3);

    std::cout << "  ✓ Linear DAG test passed!" << std::endl;
}

void test_simple_cycle() {
    std::cout << "[TEST] Running 3-node Cycle test..." << std::endl;
    Graph g;
    // A depends on B (B -> A)
    // B depends on C (C -> B)
    // C depends on A (A -> C)
    // Cycle: A -> C -> B -> A
    g.add_dependency("A", "B");
    g.add_dependency("B", "C");
    g.add_dependency("C", "A");

    assert(g.get_num_vertices() == 3);
    assert(g.get_num_edges() == 3);

    KosarajuAlgorithm kosaraju(g);
    KosarajuResult res = kosaraju.run();

    assert(res.total_sccs == 1);
    assert(res.cycle_count == 1);
    assert(res.has_cycles);
    assert(res.sccs[0].is_cycle);
    assert(res.sccs[0].module_names.size() == 3);

    CondensationGraph cond(g, res.sccs);
    assert(cond.get_num_components() == 1);

    KahnTopologicalSort kahn(cond);
    TopologicalSortResult topo = kahn.run();
    assert(topo.is_dag);
    assert(topo.component_order.size() == 1);

    std::cout << "  ✓ 3-node Cycle test passed!" << std::endl;
}

void test_self_loop() {
    std::cout << "[TEST] Running Self-Loop test..." << std::endl;
    Graph g;
    // Module X depends on X (X -> X)
    g.add_dependency("X", "X");

    assert(g.get_num_vertices() == 1);
    assert(g.get_num_edges() == 1);
    assert(g.has_self_loop(0));

    KosarajuAlgorithm kosaraju(g);
    KosarajuResult res = kosaraju.run();

    assert(res.total_sccs == 1);
    assert(res.cycle_count == 1);
    assert(res.has_cycles);
    assert(res.sccs[0].is_cycle);
    assert(res.sccs[0].cycle_type == "SELF_LOOP");

    std::cout << "  ✓ Self-Loop test passed!" << std::endl;
}

void test_disconnected_and_multiple_cycles() {
    std::cout << "[TEST] Running Disconnected & Multiple Cycles test..." << std::endl;
    Graph g;
    // Component 1 (Cycle): A <-> B
    g.add_dependency("A", "B");
    g.add_dependency("B", "A");

    // Component 2 (Cycle): C <-> D
    g.add_dependency("C", "D");
    g.add_dependency("D", "C");

    // Component 3 (Isolated): E
    g.add_vertex("E");

    assert(g.get_num_vertices() == 5);

    KosarajuAlgorithm kosaraju(g);
    KosarajuResult res = kosaraju.run();

    assert(res.total_sccs == 3);
    assert(res.cycle_count == 2);
    assert(res.acyclic_count == 1);
    assert(res.has_cycles);

    CondensationGraph cond(g, res.sccs);
    assert(cond.get_num_components() == 3);

    KahnTopologicalSort kahn(cond);
    TopologicalSortResult topo = kahn.run();
    assert(topo.is_dag);
    assert(topo.component_order.size() == 3);

    std::cout << "  ✓ Disconnected & Multiple Cycles test passed!" << std::endl;
}

void test_condensation_dag_validity() {
    std::cout << "[TEST] Running Condensation DAG Validity test..." << std::endl;
    Graph g;
    // Cycle 1: A, B (A depends on B, B depends on A)
    g.add_dependency("A", "B");
    g.add_dependency("B", "A");

    // Cycle 2: C, D (C depends on D, D depends on C)
    g.add_dependency("C", "D");
    g.add_dependency("D", "C");

    // Dependency from Cycle 1 to Cycle 2: C depends on B (B -> C)
    // Edge in graph: B -> C
    g.add_dependency("C", "B");

    // Downstream node E depends on D (D -> E)
    g.add_dependency("E", "D");

    KosarajuAlgorithm kosaraju(g);
    KosarajuResult res = kosaraju.run();

    assert(res.total_sccs == 3); // {A,B}, {C,D}, {E}
    assert(res.cycle_count == 2);

    CondensationGraph cond(g, res.sccs);
    assert(cond.get_num_components() == 3);

    // Verify condensation edges: {A,B} -> {C,D} -> {E}
    KahnTopologicalSort kahn(cond);
    TopologicalSortResult topo = kahn.run();
    assert(topo.is_dag);
    assert(topo.component_order.size() == 3);

    // Topological order must place {A,B} before {C,D}, and {C,D} before {E}
    int scc_ab = -1, scc_cd = -1, scc_e = -1;
    for (int scc_id = 0; scc_id < 3; ++scc_id) {
        const auto& node = cond.get_node(scc_id);
        for (const auto& mod : node.module_names) {
            if (mod == "A") scc_ab = scc_id;
            if (mod == "C") scc_cd = scc_id;
            if (mod == "E") scc_e = scc_id;
        }
    }

    auto pos_ab = std::find(topo.component_order.begin(), topo.component_order.end(), scc_ab);
    auto pos_cd = std::find(topo.component_order.begin(), topo.component_order.end(), scc_cd);
    auto pos_e = std::find(topo.component_order.begin(), topo.component_order.end(), scc_e);

    assert(pos_ab < pos_cd);
    assert(pos_cd < pos_e);

    std::cout << "  ✓ Condensation DAG Validity test passed!" << std::endl;
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "   RUNNING C++ DSA ALGORITHM TEST SUITE " << std::endl;
    std::cout << "========================================" << std::endl;

    test_linear_dag();
    test_simple_cycle();
    test_self_loop();
    test_disconnected_and_multiple_cycles();
    test_condensation_dag_validity();

    std::cout << "\n========================================" << std::endl;
    std::cout << "   ALL C++ ALGORITHM TESTS PASSED!       " << std::endl;
    std::cout << "========================================" << std::endl;
    return 0;
}
