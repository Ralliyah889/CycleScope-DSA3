#include "kosaraju.h"
#include <algorithm>

KosarajuAlgorithm::KosarajuAlgorithm(const Graph& g) : graph(g), V(g.get_num_vertices()) {}

void KosarajuAlgorithm::dfs1(int u, std::vector<bool>& visited, std::stack<int>& finish_stack,
                             std::vector<int>& finishing_order, std::vector<DfsStep>& trace) {
    visited[u] = true;
    std::string u_name = graph.get_vertex_name(u);

    // Record ENTER step
    trace.push_back({
        "ENTER", u, u_name, -1, "", {},
        "Visiting module " + u_name + " in First DFS (discovering outgoing dependencies)"
    });

    // Explore all outgoing edges (u -> v)
    for (int v : graph.get_neighbors(u)) {
        std::string v_name = graph.get_vertex_name(v);
        if (!visited[v]) {
            trace.push_back({
                "EXPLORE_EDGE", u, u_name, v, v_name, {},
                "Traversing dependency edge from " + u_name + " -> " + v_name
            });
            dfs1(v, visited, finish_stack, finishing_order, trace);
        } else {
            trace.push_back({
                "EDGE_ALREADY_VISITED", u, u_name, v, v_name, {},
                "Module " + v_name + " was already visited; skipping"
            });
        }
    }

    // All outgoing edges from u have finished processing
    finish_stack.push(u);
    finishing_order.push_back(u);

    // Create a snapshot of current stack for UI visualization
    std::stack<int> temp_stack = finish_stack;
    std::vector<std::string> stack_snap;
    while (!temp_stack.empty()) {
        stack_snap.push_back(graph.get_vertex_name(temp_stack.top()));
        temp_stack.pop();
    }
    std::reverse(stack_snap.begin(), stack_snap.end()); // Bottom to top

    trace.push_back({
        "PUSH_STACK", u, u_name, -1, "", stack_snap,
        "Module " + u_name + " finished exploration. Pushed to finishing stack (Kosaraju Step 1)."
    });
}

std::vector<std::vector<int>> KosarajuAlgorithm::compute_transpose() const {
    std::vector<std::vector<int>> adj_rev(V);
    for (int u = 0; u < V; ++u) {
        for (int v : graph.get_neighbors(u)) {
            // Original edge: u -> v
            // Transposed edge: v -> u
            adj_rev[v].push_back(u);
        }
    }
    return adj_rev;
}

void KosarajuAlgorithm::dfs2(int u, const std::vector<std::vector<int>>& adj_rev,
                             std::vector<bool>& visited, std::vector<int>& current_scc,
                             int scc_id, std::vector<DfsStep>& trace) {
    visited[u] = true;
    current_scc.push_back(u);
    std::string u_name = graph.get_vertex_name(u);

    trace.push_back({
        "SCC_MEMBER", u, u_name, -1, "", {},
        "Discovered module " + u_name + " belonging to Component " + std::to_string(scc_id)
    });

    for (int v : adj_rev[u]) {
        std::string v_name = graph.get_vertex_name(v);
        if (!visited[v]) {
            trace.push_back({
                "EXPLORE_TRANSPOSE_EDGE", u, u_name, v, v_name, {},
                "Following reversed edge " + u_name + " -> " + v_name + " in G^T"
            });
            dfs2(v, adj_rev, visited, current_scc, scc_id, trace);
        }
    }
}

KosarajuResult KosarajuAlgorithm::run() {
    KosarajuResult result;
    if (V == 0) {
        result.total_sccs = 0;
        result.cycle_count = 0;
        result.acyclic_count = 0;
        result.has_cycles = false;
        return result;
    }

    // ==========================================
    // STAGE 1: First DFS to obtain finishing times
    // ==========================================
    std::vector<bool> visited(V, false);
    std::stack<int> finish_stack;

    for (int u = 0; u < V; ++u) {
        if (!visited[u]) {
            dfs1(u, visited, finish_stack, result.finishing_order, result.stage1_trace);
        }
    }

    for (int id : result.finishing_order) {
        result.finishing_order_names.push_back(graph.get_vertex_name(id));
    }

    // ==========================================
    // STAGE 2: Construct Transposed Graph (G^T)
    // ==========================================
    result.transposed_adj = compute_transpose();
    for (int u = 0; u < V; ++u) {
        for (int v : result.transposed_adj[u]) {
            result.transposed_edges.push_back({u, v});
        }
    }

    // ==========================================
    // STAGE 3: Second DFS on Transposed Graph
    // in order of decreasing finishing times
    // ==========================================
    std::fill(visited.begin(), visited.end(), false);
    int current_scc_id = 0;
    result.cycle_count = 0;
    result.acyclic_count = 0;

    while (!finish_stack.empty()) {
        int u = finish_stack.top();
        finish_stack.pop();

        if (!visited[u]) {
            std::vector<int> current_scc_vertices;
            result.stage3_trace.push_back({
                "START_SCC", u, graph.get_vertex_name(u), -1, "", {},
                "Popped " + graph.get_vertex_name(u) + " from stack with highest finishing time. Starting new SCC " + std::to_string(current_scc_id)
            });

            dfs2(u, result.transposed_adj, visited, current_scc_vertices, current_scc_id, result.stage3_trace);

            // Construct SCC object
            SCC scc;
            scc.id = current_scc_id;
            scc.vertex_ids = current_scc_vertices;
            for (int vid : current_scc_vertices) {
                scc.module_names.push_back(graph.get_vertex_name(vid));
            }

            // Circular dependency detection:
            // 1. Multiple modules mutually dependent (size > 1)
            // 2. Single module depending on itself (self-loop)
            if (current_scc_vertices.size() > 1) {
                scc.is_cycle = true;
                scc.cycle_type = "MUTUAL_CYCLE";
                result.cycle_count++;
            } else if (current_scc_vertices.size() == 1 && graph.has_self_loop(current_scc_vertices[0])) {
                scc.is_cycle = true;
                scc.cycle_type = "SELF_LOOP";
                result.cycle_count++;
            } else {
                scc.is_cycle = false;
                scc.cycle_type = "ACYCLIC";
                result.acyclic_count++;
            }

            result.sccs.push_back(scc);
            current_scc_id++;
        }
    }

    result.total_sccs = static_cast<int>(result.sccs.size());
    result.has_cycles = (result.cycle_count > 0);

    return result;
}
