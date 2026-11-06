#include "condensation.h"
#include <sstream>

CondensationGraph::CondensationGraph(const Graph& g, const std::vector<SCC>& sccs)
    : num_components(static_cast<int>(sccs.size())) {

    int total_vertices = g.get_num_vertices();
    vertex_to_scc.assign(total_vertices, -1);
    nodes.resize(num_components);
    comp_adj.resize(num_components);
    in_degrees.assign(num_components, 0);

    // 1. Map each vertex to its SCC and initialize condensation nodes
    for (int i = 0; i < num_components; ++i) {
        const auto& scc = sccs[i];
        nodes[i].scc_id = scc.id;
        nodes[i].vertex_ids = scc.vertex_ids;
        nodes[i].module_names = scc.module_names;
        nodes[i].is_cycle = scc.is_cycle;
        nodes[i].cycle_type = scc.cycle_type;
        nodes[i].in_degree = 0;
        nodes[i].out_degree = 0;

        // Create readable label, e.g. "SCC_0 {A, B, C}"
        std::stringstream ss;
        ss << "SCC_" << scc.id << " {";
        for (size_t m = 0; m < scc.module_names.size(); ++m) {
            if (m > 0) ss << ", ";
            ss << scc.module_names[m];
        }
        ss << "}";
        nodes[i].label = ss.str();

        for (int vid : scc.vertex_ids) {
            if (vid >= 0 && vid < total_vertices) {
                vertex_to_scc[vid] = i;
            }
        }
    }

    // 2. Add edges between distinct SCCs (avoiding duplicates)
    std::set<std::pair<int, int>> unique_edges;

    for (const auto& edge : g.get_edge_list()) {
        int u = edge.first;
        int v = edge.second;

        if (u < 0 || u >= total_vertices || v < 0 || v >= total_vertices) continue;

        int cu = vertex_to_scc[u];
        int cv = vertex_to_scc[v];

        if (cu != -1 && cv != -1 && cu != cv) {
            if (unique_edges.find({cu, cv}) == unique_edges.end()) {
                unique_edges.insert({cu, cv});
                comp_adj[cu].push_back(cv);
                comp_edges.push_back({cu, cv});
                in_degrees[cv]++;
                nodes[cv].in_degree++;
                nodes[cu].out_degree++;
            }
        }
    }
}

int CondensationGraph::get_num_components() const {
    return num_components;
}

const std::vector<CondensationNode>& CondensationGraph::get_nodes() const {
    return nodes;
}

const CondensationNode& CondensationGraph::get_node(int scc_id) const {
    return nodes[scc_id];
}

int CondensationGraph::get_scc_for_vertex(int vertex_id) const {
    if (vertex_id >= 0 && vertex_id < static_cast<int>(vertex_to_scc.size())) {
        return vertex_to_scc[vertex_id];
    }
    return -1;
}

const std::vector<int>& CondensationGraph::get_component_neighbors(int scc_id) const {
    return comp_adj[scc_id];
}

const std::vector<std::vector<int>>& CondensationGraph::get_adjacency_list() const {
    return comp_adj;
}

const std::vector<std::pair<int, int>>& CondensationGraph::get_edge_list() const {
    return comp_edges;
}

const std::vector<int>& CondensationGraph::get_in_degrees() const {
    return in_degrees;
}
