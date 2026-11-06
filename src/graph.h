#ifndef GRAPH_H
#define GRAPH_H

#include <string>
#include <vector>
#include <unordered_map>
#include <utility>

/**
 * Directed Graph Data Structure for Software Modules.
 * 
 * Vertices: Software module names (string).
 * Edges: Directed dependencies.
 * 
 * Convention:
 * If module A depends on module B, an edge is created: B -> A
 * Meaning: Module B must be processed / compiled before Module A.
 */
class Graph {
private:
    int num_vertices;
    std::unordered_map<std::string, int> name_to_id;
    std::vector<std::string> id_to_name;
    std::vector<std::vector<int>> adj;
    std::vector<std::pair<int, int>> edge_list; // original directed edges (u -> v)
    std::vector<std::pair<std::string, std::string>> raw_dependencies; // (Module, Depends_On)

public:
    Graph();

    // Adds a module vertex if not present, returns its integer ID
    int add_vertex(const std::string& name);

    // Adds a dependency: module "module" depends on "depends_on"
    // Edge created: depends_on -> module
    void add_dependency(const std::string& module_name, const std::string& depends_on);

    // Directly add directed edge u -> v by ID
    void add_edge_by_id(int u, int v);

    // Graph queries
    int get_num_vertices() const;
    int get_num_edges() const;
    int get_vertex_id(const std::string& name) const;
    std::string get_vertex_name(int id) const;
    const std::vector<int>& get_neighbors(int u) const;
    const std::vector<std::vector<int>>& get_adjacency_list() const;
    const std::vector<std::pair<int, int>>& get_edge_list() const;
    const std::vector<std::string>& get_all_vertex_names() const;
    const std::vector<std::pair<std::string, std::string>>& get_raw_dependencies() const;

    // Checks if vertex has a self-loop (u -> u)
    bool has_self_loop(int u) const;

    // Load graph from CSV file
    // Format: Module,Depends_On
    bool load_from_csv(const std::string& filepath, std::string& error_msg);
};

#endif // GRAPH_H
