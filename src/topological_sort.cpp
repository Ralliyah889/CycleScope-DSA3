#include "topological_sort.h"
#include <algorithm>
#include <sstream>

KahnTopologicalSort::KahnTopologicalSort(const CondensationGraph& cg)
    : cond_graph(cg), K(cg.get_num_components()) {}

TopologicalSortResult KahnTopologicalSort::run() {
    TopologicalSortResult result;
    if (K == 0) {
        result.is_dag = true;
        result.explanation = "Graph is empty; no execution order needed.";
        return result;
    }

    std::vector<int> in_deg = cond_graph.get_in_degrees();
    std::vector<int> depth(K, 0); // For grouping into parallel phases
    std::queue<int> q;

    // Helper to snapshot queue
    auto get_queue_snapshot = [](std::queue<int> temp_q) {
        std::vector<int> snap;
        while (!temp_q.empty()) {
            snap.push_back(temp_q.front());
            temp_q.pop();
        }
        return snap;
    };

    // 1. Enqueue all components with in-degree 0 (no prerequisites)
    for (int i = 0; i < K; ++i) {
        if (in_deg[i] == 0) {
            q.push(i);
        }
    }

    int step_counter = 1;

    // 2. Process queue
    while (!q.empty()) {
        int u = q.front();
        q.pop();

        result.component_order.push_back(u);
        const auto& u_node = cond_graph.get_node(u);
        result.component_labels.push_back(u_node.label);

        KahnStep step;
        step.step_number = step_counter++;
        step.dequeued_scc = u;
        step.dequeued_label = u_node.label;
        step.modules = u_node.module_names;

        std::stringstream ss_note;
        ss_note << "Processing " << u_node.label << " (in-degree is 0; all prerequisites satisfied). ";

        std::vector<int> newly_ready;

        // Decrement in-degree for all downstream neighbors
        for (int v : cond_graph.get_component_neighbors(u)) {
            depth[v] = std::max(depth[v], depth[u] + 1);
            in_deg[v]--;
            if (in_deg[v] == 0) {
                q.push(v);
                newly_ready.push_back(v);
            }
        }

        if (!newly_ready.empty()) {
            ss_note << "Updated downstream in-degrees. Ready to queue: ";
            for (size_t nr = 0; nr < newly_ready.size(); ++nr) {
                if (nr > 0) ss_note << ", ";
                ss_note << cond_graph.get_node(newly_ready[nr]).label;
            }
        } else {
            ss_note << "No new components reached in-degree 0 in this step.";
        }

        step.note = ss_note.str();
        step.queue_snapshot = get_queue_snapshot(q);
        for (int q_item : step.queue_snapshot) {
            step.queue_snapshot_labels.push_back(cond_graph.get_node(q_item).label);
        }

        for (int i = 0; i < K; ++i) {
            step.current_in_degrees[i] = in_deg[i];
        }

        result.kahn_steps.push_back(step);
    }

    result.is_dag = (static_cast<int>(result.component_order.size()) == K);

    // 3. Construct phased parallel execution groups
    int max_depth = 0;
    for (int d : depth) {
        if (d > max_depth) max_depth = d;
    }

    result.phases.resize(max_depth + 1);
    for (int i = 0; i <= max_depth; ++i) {
        result.phases[i].phase_number = i + 1;
        result.phases[i].contains_cycles = false;
    }

    for (int scc_id : result.component_order) {
        int d = depth[scc_id];
        const auto& node = cond_graph.get_node(scc_id);
        result.phases[d].scc_ids.push_back(scc_id);
        result.phases[d].scc_labels.push_back(node.label);
        for (const auto& mod : node.module_names) {
            result.phases[d].all_modules_in_phase.push_back(mod);
        }
        if (node.is_cycle) {
            result.phases[d].contains_cycles = true;
        }
    }

    for (auto& phase : result.phases) {
        std::stringstream ss;
        if (phase.contains_cycles) {
            ss << "Phase " << phase.phase_number << " contains circular dependency group(s). "
               << "Mutual dependencies inside the cycle must be co-compiled or decoupled.";
        } else {
            ss << "Phase " << phase.phase_number << " modules have all dependencies fulfilled. "
               << "They can be compiled or processed concurrently.";
        }
        phase.explanation = ss.str();
    }

    if (result.is_dag) {
        result.explanation = "Successfully computed topological execution order for the Condensation DAG using Kahn's algorithm.";
    } else {
        result.explanation = "Error: Cycle detected in Condensation Graph (this should not occur mathematically).";
    }

    return result;
}
