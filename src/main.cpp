#include "graph.h"
#include "kosaraju.h"
#include "condensation.h"
#include "topological_sort.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>

namespace {
    // Helper to safely escape characters for JSON
    std::string escape_json(const std::string& s) {
        std::ostringstream o;
        for (char c : s) {
            switch (c) {
                case '"':  o << "\\\""; break;
                case '\\': o << "\\\\"; break;
                case '\b': o << "\\b";  break;
                case '\f': o << "\\f";  break;
                case '\n': o << "\\n";  break;
                case '\r': o << "\\r";  break;
                case '\t': o << "\\t";  break;
                default:
                    if ('\x00' <= c && c <= '\x1f') {
                        o << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(c);
                    } else {
                        o << c;
                    }
            }
        }
        return o.str();
    }

    void print_text_summary(const Graph& g, const KosarajuResult& scc_res,
                            const CondensationGraph& cond, const TopologicalSortResult& topo_res) {
        std::cout << "\n=======================================================\n";
        std::cout << " SOFTWARE DEPENDENCY CYCLE ANALYZER (C++ DSA ENGINE)\n";
        std::cout << "=======================================================\n\n";

        std::cout << "[GRAPH OVERVIEW]\n";
        std::cout << "  Total Modules:      " << g.get_num_vertices() << "\n";
        std::cout << "  Total Dependencies: " << g.get_num_edges() << "\n";
        std::cout << "  Has Cycles:         " << (scc_res.has_cycles ? "YES (Circular Dependencies Detected!)" : "NO (Clean DAG)") << "\n";
        std::cout << "  Cycle Groups:       " << scc_res.cycle_count << "\n";
        std::cout << "  Acyclic Modules:    " << scc_res.acyclic_count << "\n\n";

        std::cout << "[KOSARAJU SCC DISCOVERY]\n";
        for (const auto& scc : scc_res.sccs) {
            std::cout << "  SCC " << scc.id << " [";
            if (scc.is_cycle) {
                std::cout << "CYCLE - " << scc.cycle_type << "]: ";
            } else {
                std::cout << "INDEPENDENT]: ";
            }
            for (size_t m = 0; m < scc.module_names.size(); ++m) {
                if (m > 0) std::cout << ", ";
                std::cout << scc.module_names[m];
            }
            std::cout << "\n";
        }

        std::cout << "\n[CONDENSATION DAG EDGES]\n";
        const auto& cond_edges = cond.get_edge_list();
        if (cond_edges.empty()) {
            std::cout << "  No cross-component dependencies.\n";
        } else {
            for (const auto& edge : cond_edges) {
                std::cout << "  SCC_" << edge.first << " -> SCC_" << edge.second << "\n";
            }
        }

        std::cout << "\n[TOPOLOGICAL EXECUTION ORDER (KAHN'S ALGORITHM)]\n";
        for (const auto& phase : topo_res.phases) {
            std::cout << "  Phase " << phase.phase_number << ": ";
            for (size_t m = 0; m < phase.all_modules_in_phase.size(); ++m) {
                if (m > 0) std::cout << ", ";
                std::cout << phase.all_modules_in_phase[m];
            }
            if (phase.contains_cycles) {
                std::cout << "  <-- (Contains Circular Dependency!)";
            }
            std::cout << "\n";
        }
        std::cout << "\n=======================================================\n";
    }

    std::string generate_json(const Graph& g, const KosarajuResult& scc_res,
                              const CondensationGraph& cond, const TopologicalSortResult& topo_res) {
        std::ostringstream json;
        json << "{\n";
        json << "  \"status\": \"success\",\n";

        // Vertices
        json << "  \"vertices\": [";
        const auto& vnames = g.get_all_vertex_names();
        for (size_t i = 0; i < vnames.size(); ++i) {
            if (i > 0) json << ", ";
            json << "\"" << escape_json(vnames[i]) << "\"";
        }
        json << "],\n";

        // Edges: remember our edge convention B -> A means A depends on B
        json << "  \"edges\": [";
        const auto& edges = g.get_edge_list();
        for (size_t i = 0; i < edges.size(); ++i) {
            if (i > 0) json << ", ";
            std::string from_name = g.get_vertex_name(edges[i].first);
            std::string to_name = g.get_vertex_name(edges[i].second);
            json << "{\"from\": \"" << escape_json(from_name) << "\", "
                 << "\"to\": \"" << escape_json(to_name) << "\", "
                 << "\"description\": \"" << escape_json(to_name) << " depends on " << escape_json(from_name) << "\"}";
        }
        json << "],\n";

        // Summary stats
        json << "  \"stats\": {\n";
        json << "    \"total_modules\": " << g.get_num_vertices() << ",\n";
        json << "    \"total_dependencies\": " << g.get_num_edges() << ",\n";
        json << "    \"total_sccs\": " << scc_res.total_sccs << ",\n";
        json << "    \"cycle_groups_count\": " << scc_res.cycle_count << ",\n";
        json << "    \"independent_modules_count\": " << scc_res.acyclic_count << ",\n";
        json << "    \"has_cycles\": " << (scc_res.has_cycles ? "true" : "false") << "\n";
        json << "  },\n";

        // Kosaraju Stages
        json << "  \"kosaraju_stages\": {\n";

        // Stage 1
        json << "    \"stage1_finishing_order\": [";
        for (size_t i = 0; i < scc_res.finishing_order_names.size(); ++i) {
            if (i > 0) json << ", ";
            json << "\"" << escape_json(scc_res.finishing_order_names[i]) << "\"";
        }
        json << "],\n";

        json << "    \"stage1_trace\": [\n";
        for (size_t i = 0; i < scc_res.stage1_trace.size(); ++i) {
            const auto& t = scc_res.stage1_trace[i];
            if (i > 0) json << ",\n";
            json << "      {\"action\": \"" << escape_json(t.action) << "\", "
                 << "\"vertex\": \"" << escape_json(t.vertex_name) << "\", "
                 << "\"target\": \"" << escape_json(t.target_name) << "\", "
                 << "\"note\": \"" << escape_json(t.note) << "\", "
                 << "\"stack_snapshot\": [";
            for (size_t s = 0; s < t.stack_snapshot.size(); ++s) {
                if (s > 0) json << ", ";
                json << "\"" << escape_json(t.stack_snapshot[s]) << "\"";
            }
            json << "]}";
        }
        json << "\n    ],\n";

        // Stage 2
        json << "    \"stage2_transposed_edges\": [";
        for (size_t i = 0; i < scc_res.transposed_edges.size(); ++i) {
            if (i > 0) json << ", ";
            std::string from_name = g.get_vertex_name(scc_res.transposed_edges[i].first);
            std::string to_name = g.get_vertex_name(scc_res.transposed_edges[i].second);
            json << "{\"from\": \"" << escape_json(from_name) << "\", \"to\": \"" << escape_json(to_name) << "\"}";
        }
        json << "],\n";

        // Stage 3
        json << "    \"stage3_sccs\": [\n";
        for (size_t i = 0; i < scc_res.sccs.size(); ++i) {
            const auto& s = scc_res.sccs[i];
            if (i > 0) json << ",\n";
            json << "      {\"id\": " << s.id << ", "
                 << "\"is_cycle\": " << (s.is_cycle ? "true" : "false") << ", "
                 << "\"cycle_type\": \"" << escape_json(s.cycle_type) << "\", "
                 << "\"modules\": [";
            for (size_t m = 0; m < s.module_names.size(); ++m) {
                if (m > 0) json << ", ";
                json << "\"" << escape_json(s.module_names[m]) << "\"";
            }
            json << "]}";
        }
        json << "\n    ],\n";

        json << "    \"stage3_trace\": [\n";
        for (size_t i = 0; i < scc_res.stage3_trace.size(); ++i) {
            const auto& t = scc_res.stage3_trace[i];
            if (i > 0) json << ",\n";
            json << "      {\"action\": \"" << escape_json(t.action) << "\", "
                 << "\"vertex\": \"" << escape_json(t.vertex_name) << "\", "
                 << "\"note\": \"" << escape_json(t.note) << "\"}";
        }
        json << "\n    ]\n";
        json << "  },\n";

        // Condensation DAG
        json << "  \"condensation_dag\": {\n";
        json << "    \"nodes\": [\n";
        const auto& cond_nodes = cond.get_nodes();
        for (size_t i = 0; i < cond_nodes.size(); ++i) {
            const auto& cn = cond_nodes[i];
            if (i > 0) json << ",\n";
            json << "      {\"id\": " << cn.scc_id << ", "
                 << "\"label\": \"" << escape_json(cn.label) << "\", "
                 << "\"is_cycle\": " << (cn.is_cycle ? "true" : "false") << ", "
                 << "\"in_degree\": " << cn.in_degree << ", "
                 << "\"out_degree\": " << cn.out_degree << ", "
                 << "\"modules\": [";
            for (size_t m = 0; m < cn.module_names.size(); ++m) {
                if (m > 0) json << ", ";
                json << "\"" << escape_json(cn.module_names[m]) << "\"";
            }
            json << "]}";
        }
        json << "\n    ],\n";

        json << "    \"edges\": [";
        const auto& cond_edges = cond.get_edge_list();
        for (size_t i = 0; i < cond_edges.size(); ++i) {
            if (i > 0) json << ", ";
            json << "{\"from\": " << cond_edges[i].first << ", "
                 << "\"to\": " << cond_edges[i].second << ", "
                 << "\"from_label\": \"" << escape_json(cond.get_node(cond_edges[i].first).label) << "\", "
                 << "\"to_label\": \"" << escape_json(cond.get_node(cond_edges[i].second).label) << "\"}";
        }
        json << "]\n";
        json << "  },\n";

        // Topological Sort (Kahn's Algorithm)
        json << "  \"topological_sort\": {\n";
        json << "    \"is_dag\": " << (topo_res.is_dag ? "true" : "false") << ",\n";
        json << "    \"explanation\": \"" << escape_json(topo_res.explanation) << "\",\n";
        json << "    \"component_order\": [";
        for (size_t i = 0; i < topo_res.component_order.size(); ++i) {
            if (i > 0) json << ", ";
            json << topo_res.component_order[i];
        }
        json << "],\n";

        json << "    \"phases\": [\n";
        for (size_t i = 0; i < topo_res.phases.size(); ++i) {
            const auto& p = topo_res.phases[i];
            if (i > 0) json << ",\n";
            json << "      {\"phase_number\": " << p.phase_number << ", "
                 << "\"contains_cycles\": " << (p.contains_cycles ? "true" : "false") << ", "
                 << "\"explanation\": \"" << escape_json(p.explanation) << "\", "
                 << "\"scc_ids\": [";
            for (size_t s = 0; s < p.scc_ids.size(); ++s) {
                if (s > 0) json << ", ";
                json << p.scc_ids[s];
            }
            json << "], \"modules\": [";
            for (size_t m = 0; m < p.all_modules_in_phase.size(); ++m) {
                if (m > 0) json << ", ";
                json << "\"" << escape_json(p.all_modules_in_phase[m]) << "\"";
            }
            json << "]}";
        }
        json << "\n    ],\n";

        json << "    \"kahn_steps\": [\n";
        for (size_t i = 0; i < topo_res.kahn_steps.size(); ++i) {
            const auto& ks = topo_res.kahn_steps[i];
            if (i > 0) json << ",\n";
            json << "      {\"step\": " << ks.step_number << ", "
                 << "\"dequeued_scc\": " << ks.dequeued_scc << ", "
                 << "\"dequeued_label\": \"" << escape_json(ks.dequeued_label) << "\", "
                 << "\"note\": \"" << escape_json(ks.note) << "\", "
                 << "\"modules\": [";
            for (size_t m = 0; m < ks.modules.size(); ++m) {
                if (m > 0) json << ", ";
                json << "\"" << escape_json(ks.modules[m]) << "\"";
            }
            json << "], \"queue_snapshot\": [";
            for (size_t q = 0; q < ks.queue_snapshot.size(); ++q) {
                if (q > 0) json << ", ";
                json << ks.queue_snapshot[q];
            }
            json << "]}";
        }
        json << "\n    ]\n";
        json << "  }\n";

        json << "}\n";
        return json.str();
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_csv_file> [output_json_file] [--text]\n";
        return 1;
    }

    std::string input_file = argv[1];
    std::string output_file = "";
    bool text_mode = false;

    for (int i = 2; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--text") {
            text_mode = true;
        } else if (output_file.empty()) {
            output_file = arg;
        }
    }

    Graph g;
    std::string error_msg;
    if (!g.load_from_csv(input_file, error_msg)) {
        std::cerr << "{\"status\": \"error\", \"message\": \"" << escape_json(error_msg) << "\"}\n";
        return 2;
    }

    // Run Kosaraju's Algorithm
    KosarajuAlgorithm kosaraju(g);
    KosarajuResult scc_res = kosaraju.run();

    // Construct Condensation DAG
    CondensationGraph cond(g, scc_res.sccs);

    // Compute Topological Sort using Kahn's Algorithm
    KahnTopologicalSort kahn(cond);
    TopologicalSortResult topo_res = kahn.run();

    if (text_mode) {
        print_text_summary(g, scc_res, cond, topo_res);
    }

    std::string json_output = generate_json(g, scc_res, cond, topo_res);

    if (!output_file.empty()) {
        std::ofstream out(output_file);
        if (!out.is_open()) {
            std::cerr << "Could not write to output file: " << output_file << "\n";
            return 3;
        }
        out << json_output;
        out.close();
    } else if (!text_mode) {
        std::cout << json_output;
    }

    return 0;
}
