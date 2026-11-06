#include "graph.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>

namespace {
    // Helper to trim whitespace from both ends of a string
    std::string trim(const std::string& s) {
        size_t start = s.find_first_not_of(" \t\r\n");
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }

    // Helper to convert string to lowercase for case-insensitive comparison
    std::string to_lower(const std::string& s) {
        std::string res = s;
        std::transform(res.begin(), res.end(), res.begin(), [](unsigned char c) {
            return std::tolower(c);
        });
        return res;
    }
}

Graph::Graph() : num_vertices(0) {}

int Graph::add_vertex(const std::string& name) {
    std::string clean_name = trim(name);
    if (clean_name.empty()) return -1;

    auto it = name_to_id.find(clean_name);
    if (it != name_to_id.end()) {
        return it->second;
    }

    int new_id = num_vertices++;
    name_to_id[clean_name] = new_id;
    id_to_name.push_back(clean_name);
    adj.emplace_back();
    return new_id;
}

void Graph::add_dependency(const std::string& module_name, const std::string& depends_on) {
    std::string u_name = trim(module_name);
    std::string v_name = trim(depends_on);

    if (u_name.empty()) return;

    int u_id = add_vertex(u_name);

    // If dependency is empty, "none", or "-", it means the module has no prerequisites
    std::string v_lower = to_lower(v_name);
    if (v_name.empty() || v_lower == "none" || v_lower == "-" || v_lower == "null") {
        return;
    }

    int v_id = add_vertex(v_name);

    // Dependency convention:
    // If module A depends on module B: B must be built before A.
    // Edge direction: B -> A (v_id -> u_id)
    adj[v_id].push_back(u_id);
    edge_list.push_back({v_id, u_id});
    raw_dependencies.push_back({u_name, v_name});
}

void Graph::add_edge_by_id(int u, int v) {
    if (u >= 0 && u < num_vertices && v >= 0 && v < num_vertices) {
        adj[u].push_back(v);
        edge_list.push_back({u, v});
    }
}

int Graph::get_num_vertices() const {
    return num_vertices;
}

int Graph::get_num_edges() const {
    return static_cast<int>(edge_list.size());
}

int Graph::get_vertex_id(const std::string& name) const {
    auto it = name_to_id.find(trim(name));
    if (it != name_to_id.end()) {
        return it->second;
    }
    return -1;
}

std::string Graph::get_vertex_name(int id) const {
    if (id >= 0 && id < num_vertices) {
        return id_to_name[id];
    }
    return "";
}

const std::vector<int>& Graph::get_neighbors(int u) const {
    return adj[u];
}

const std::vector<std::vector<int>>& Graph::get_adjacency_list() const {
    return adj;
}

const std::vector<std::pair<int, int>>& Graph::get_edge_list() const {
    return edge_list;
}

const std::vector<std::string>& Graph::get_all_vertex_names() const {
    return id_to_name;
}

const std::vector<std::pair<std::string, std::string>>& Graph::get_raw_dependencies() const {
    return raw_dependencies;
}

bool Graph::has_self_loop(int u) const {
    if (u < 0 || u >= num_vertices) return false;
    for (int v : adj[u]) {
        if (v == u) return true;
    }
    return false;
}

bool Graph::load_from_csv(const std::string& filepath, std::string& error_msg) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        error_msg = "Could not open file: " + filepath;
        return false;
    }

    std::string line;
    bool is_first_line = true;

    while (std::getline(file, line)) {
        std::string trimmed_line = trim(line);

        // Ignore empty lines and comment lines
        if (trimmed_line.empty() || trimmed_line[0] == '#') {
            continue;
        }

        // Parse comma-separated line
        std::stringstream ss(trimmed_line);
        std::string col1, col2;

        if (!std::getline(ss, col1, ',')) {
            continue;
        }
        std::getline(ss, col2); // remainder is col2

        col1 = trim(col1);
        col2 = trim(col2);

        // Check if first line is a header
        if (is_first_line) {
            is_first_line = false;
            std::string c1_lower = to_lower(col1);
            std::string c2_lower = to_lower(col2);
            if ((c1_lower == "module" || c1_lower == "source" || c1_lower == "from") &&
                (c2_lower == "depends_on" || c2_lower == "dependency" || c2_lower == "target" || c2_lower == "to")) {
                continue; // Skip header
            }
        }

        if (col1.empty()) {
            continue;
        }

        // Add to graph
        add_dependency(col1, col2);
    }

    file.close();

    if (num_vertices == 0) {
        error_msg = "File contained no valid module records.";
        return false;
    }

    return true;
}
