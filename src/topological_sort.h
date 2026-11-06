#ifndef TOPOLOGICAL_SORT_H
#define TOPOLOGICAL_SORT_H

#include "condensation.h"
#include <vector>
#include <string>
#include <queue>
#include <map>

// Step trace for Kahn's algorithm visualization
struct KahnStep {
    int step_number;
    int dequeued_scc;
    std::string dequeued_label;
    std::vector<std::string> modules;
    std::vector<int> queue_snapshot;
    std::vector<std::string> queue_snapshot_labels;
    std::map<int, int> current_in_degrees;
    std::string note;
};

// Represents one execution phase / batch (can run in parallel)
struct ExecutionPhase {
    int phase_number;
    std::vector<int> scc_ids;
    std::vector<std::string> scc_labels;
    std::vector<std::string> all_modules_in_phase;
    bool contains_cycles;
    std::string explanation;
};

// Complete result of Topological Sorting on Condensation Graph
struct TopologicalSortResult {
    bool is_dag;                                 // Should always be true for condensation graph
    std::vector<int> component_order;            // SCC IDs in topological order
    std::vector<std::string> component_labels;   // SCC labels in order
    std::vector<ExecutionPhase> phases;          // Parallel execution phases / levels
    std::vector<KahnStep> kahn_steps;            // Step-by-step trace of Kahn's algorithm
    std::string explanation;
};

class KahnTopologicalSort {
private:
    const CondensationGraph& cond_graph;
    int K;

public:
    explicit KahnTopologicalSort(const CondensationGraph& cg);

    // Executes Kahn's algorithm using in-degrees and std::queue
    TopologicalSortResult run();
};

#endif // TOPOLOGICAL_SORT_H
