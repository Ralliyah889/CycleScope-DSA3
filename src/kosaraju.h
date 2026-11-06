#ifndef KOSARAJU_H
#define KOSARAJU_H

#include "graph.h"
#include <vector>
#include <stack>
#include <string>

// Structure to capture step-by-step trace of DFS for visualization
struct DfsStep {
    std::string action;       // "ENTER", "EXPLORE_EDGE", "BACKTRACK", "PUSH_STACK", "SCC_MEMBER"
    int vertex;               // Vertex ID
    std::string vertex_name;  // Vertex module name
    int target_vertex;        // Target vertex if exploring edge (-1 if not applicable)
    std::string target_name;  // Target vertex name
    std::vector<std::string> stack_snapshot; // Snapshot of stack (for Step 1)
    std::string note;         // Explanatory note for viva/learning
};

// Represents one Strongly Connected Component
struct SCC {
    int id;                                // Component ID (0, 1, 2...)
    std::vector<int> vertex_ids;          // Vertex IDs inside component
    std::vector<std::string> module_names;// Module names inside component
    bool is_cycle;                        // True if size > 1 or self-loop
    std::string cycle_type;               // "MUTUAL_CYCLE", "SELF_LOOP", "ACYCLIC"
};

// Complete results of Kosaraju's Algorithm
struct KosarajuResult {
    // Stage 1: First DFS finishing order
    std::vector<int> finishing_order;             // Order vertices finished in DFS 1
    std::vector<std::string> finishing_order_names;
    std::vector<DfsStep> stage1_trace;

    // Stage 2: Transpose Graph
    std::vector<std::vector<int>> transposed_adj;
    std::vector<std::pair<int, int>> transposed_edges;

    // Stage 3: Second DFS and Discovered SCCs
    std::vector<SCC> sccs;
    std::vector<DfsStep> stage3_trace;

    // Summary statistics
    int total_sccs;
    int cycle_count;
    int acyclic_count;
    bool has_cycles;
};

class KosarajuAlgorithm {
private:
    const Graph& graph;
    int V;

    // Helper for DFS 1
    void dfs1(int u, std::vector<bool>& visited, std::stack<int>& finish_stack,
              std::vector<int>& finishing_order, std::vector<DfsStep>& trace);

    // Helper for DFS 2
    void dfs2(int u, const std::vector<std::vector<int>>& adj_rev,
              std::vector<bool>& visited, std::vector<int>& current_scc,
              int scc_id, std::vector<DfsStep>& trace);

public:
    explicit KosarajuAlgorithm(const Graph& g);

    // Executes all 3 stages of Kosaraju's algorithm
    KosarajuResult run();

    // Stage 2 standalone helper: construct transpose graph
    std::vector<std::vector<int>> compute_transpose() const;
};

#endif // KOSARAJU_H
