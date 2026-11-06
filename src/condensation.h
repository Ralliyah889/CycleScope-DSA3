#ifndef CONDENSATION_H
#define CONDENSATION_H

#include "graph.h"
#include "kosaraju.h"
#include <vector>
#include <string>
#include <set>

// Represents one super-node in the Condensation DAG
struct CondensationNode {
    int scc_id;
    std::string label;                       // e.g. "SCC_0: [A, B, C]"
    std::vector<int> vertex_ids;
    std::vector<std::string> module_names;
    bool is_cycle;
    std::string cycle_type;
    int in_degree;
    int out_degree;
};

// Represents the Condensation DAG
class CondensationGraph {
private:
    int num_components;
    std::vector<CondensationNode> nodes;
    std::vector<int> vertex_to_scc; // Maps each original vertex ID -> SCC ID
    std::vector<std::vector<int>> comp_adj; // Component adjacency list (no duplicates)
    std::vector<std::pair<int, int>> comp_edges; // Component edge list (u -> v)
    std::vector<int> in_degrees;

public:
    CondensationGraph(const Graph& g, const std::vector<SCC>& sccs);

    int get_num_components() const;
    const std::vector<CondensationNode>& get_nodes() const;
    const CondensationNode& get_node(int scc_id) const;
    int get_scc_for_vertex(int vertex_id) const;
    const std::vector<int>& get_component_neighbors(int scc_id) const;
    const std::vector<std::vector<int>>& get_adjacency_list() const;
    const std::vector<std::pair<int, int>>& get_edge_list() const;
    const std::vector<int>& get_in_degrees() const;
};

#endif // CONDENSATION_H
