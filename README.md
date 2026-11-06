# CycleScope: Software Dependency Cycle Analyzer

## 1. Project Introduction

CycleScope is a Data Structures and Algorithms mini project that analyzes dependencies between software modules and identifies circular dependencies. The modules are represented as vertices in a directed graph, and their dependencies are represented as directed edges.

The project uses **Kosaraju's algorithm** to identify Strongly Connected Components (SCCs). Components containing multiple modules or a self-loop represent circular dependencies. These components are then combined into a Condensation Directed Acyclic Graph (DAG). Kahn's algorithm is applied to the resulting DAG to determine a valid execution order.

A Streamlit application provides an interactive interface to upload dependency data, visualize the graph, observe the algorithm stages, inspect circular dependency groups, and explore the resulting execution order.

The project uses a manually implemented C++ graph engine. No external graph algorithm library is used.

## 2. Problem Statement

Software projects contain multiple modules that depend on one another. As the number of modules increases, managing their dependencies and determining a valid execution order becomes difficult.

Circular dependencies occur when a group of modules directly or indirectly depends on one another. For example:

A → B → C → A

In this case, all three modules belong to the same Strongly Connected Component. They cannot be independently arranged in a topological order.

This project explores how graph algorithms can identify these circular relationships, group mutually dependent modules, and construct a dependency structure that supports a valid execution order.

## 3. Objectives

- Represent software modules and their dependencies using a directed graph.
- Store graph connections using an adjacency list.
- Implement Depth First Search (DFS) for graph traversal.
- Identify Strongly Connected Components using Kosaraju's algorithm.
- Detect circular dependencies, including self-loops.
- Construct a Condensation DAG by grouping SCCs.
- Apply Kahn's algorithm to determine a valid topological order.
- Visualize graph relationships and algorithm execution through a Streamlit interface.
- Provide test cases for different graph structures and edge cases.

## 4. Technologies Used

| Technology | Role in this project |
|---|---|
| C++17 | Implementation of graph data structures and algorithms |
| Python | Application integration and data handling |
| Streamlit | Interactive web interface |
| Graphviz | Directed graph visualization |
| Pytest | Automated application tests |
| Makefile / g++ | Compilation of the C++ engine |

The core graph algorithms, including Kosaraju's SCC detection and Kahn's topological sorting, are implemented manually in C++ without using external graph algorithm libraries.

## 5. Algorithms Used

**Graph Representation:** Software modules are represented as vertices, and dependencies are stored as directed edges using an adjacency list. If module A depends on module B, the edge is represented as B → A, indicating that B must be processed before A.

**Depth First Search (DFS):** DFS explores vertices by visiting their unvisited adjacent vertices. It is used in both traversals of Kosaraju's algorithm.

**Kosaraju's Algorithm:** Identifies Strongly Connected Components using two DFS traversals. The first traversal records vertices according to their finishing order. The graph is then transposed, and the second traversal identifies the SCCs.

**Graph Transpose:** Creates a new graph by reversing the direction of every edge in the original graph.

**Circular Dependency Detection:** An SCC containing more than one vertex represents a circular dependency. A single-vertex SCC is also circular if the vertex has an edge to itself.

**Condensation DAG:** Each SCC is represented as a single component vertex. Edges between different components are retained, while internal edges are removed and duplicate component edges are avoided. The resulting graph is a DAG.

**Kahn's Topological Sorting:** Uses indegrees and a queue to process zero-indegree components first. As components are processed, the indegrees of their neighboring components are updated until a valid topological order is obtained.

## 6. Graph and Kosaraju's Algorithm Explanation

A directed graph consists of vertices connected by edges that have a specific direction.

In CycleScope:

- Vertices represent software modules.
- Directed edges represent dependency relationships.
- An edge B → A means module A depends on module B.

Kosaraju's algorithm identifies SCCs in three steps.

**Step 1: First DFS Traversal**

DFS is performed on the original graph. After all adjacent vertices of a vertex have been visited, that vertex is pushed onto a stack.

The stack stores vertices according to their finishing order.

**Step 2: Transpose Graph**

Every edge in the original graph is reversed to create the transposed graph.

For example:

Original: A → B

Transposed: B → A

**Step 3: Second DFS Traversal**

Vertices are processed in decreasing order of finishing time. DFS is performed on the transposed graph, and each traversal identifies one Strongly Connected Component.

For example, consider:

A → B

B → C

C → A

All three vertices are mutually reachable and therefore form one SCC:

SCC = {A, B, C}

Since the component contains more than one module, it represents a circular dependency group.

## 7. Condensation DAG and Topological Sorting

After identifying all Strongly Connected Components, CycleScope constructs a Condensation DAG.

Each SCC is treated as a single component. Connections between different components are retained, while edges inside the same component are removed.

For example, consider:

- SCC 0 = {A, B, C}
- SCC 1 = {D}
- SCC 2 = {E}

If the dependency relationships connect these components in sequence, the condensed graph represents them as separate component vertices.

The resulting graph is guaranteed to be acyclic.

**Kahn's Algorithm**

The Condensation DAG is processed using Kahn's topological sorting algorithm.

The algorithm works as follows:

1. Calculate the indegree of every component.
2. Insert all components with indegree zero into a queue.
3. Remove a component from the queue and add it to the execution order.
4. Decrease the indegree of its neighboring components.
5. Insert newly zero-indegree components into the queue.
6. Continue until all components have been processed.

Components that become available at the same execution level can be processed in parallel.

A cyclic SCC is treated as a single group because its internal modules cannot be independently topologically ordered.

## 8. System Workflow

1. The application accepts dependency data through a CSV file.
2. The uploaded data is validated and processed.
3. Software modules are identified and stored as graph vertices.
4. Dependencies are converted into directed edges.
5. An adjacency list is constructed in the C++ graph engine.
6. The first DFS traversal records the finishing order of vertices.
7. The graph is transposed by reversing all edges.
8. The second DFS traversal identifies Strongly Connected Components.
9. Circular dependency groups and self-loops are identified.
10. The SCCs are combined to construct the Condensation DAG.
11. Kahn's algorithm calculates a valid topological execution order.
12. The application displays the graph, SCC groups, condensed DAG, and execution phases.


## 9. Installation Instructions

Use Python 3.10 or newer and a C++17-compatible compiler.

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment using:

```bash
.venv\Scripts\activate
```

Make sure that a C++17-compatible compiler is available.

## 10. How to Run the Application

Compile the C++ engine using the provided Makefile:

```bash
make
```

Start the Streamlit application:

```bash
streamlit run app.py
```

The application opens in a browser.

Users can upload a dependency CSV file or load the included sample dataset to explore the graph analysis.

Run the automated tests using:

```bash
pytest -q
```

## 11. Sample Input and Output

The application accepts dependency information in CSV format with two columns: `Module` and `Depends_On`.

**Sample Input**

```csv
Module,Depends_On
A,B
B,C
C,A
D,C
E,D
F,E
G,F
```

**Explanation**

- A depends on B.
- B depends on C.
- C depends on A.
- D depends on C.
- E depends on D.
- F depends on E.
- G depends on F.

**Expected SCC Groups**

```text
SCC 0: {A, B, C}
SCC 1: {D}
SCC 2: {E}
SCC 3: {F}
SCC 4: {G}
```

**Circular Dependency Analysis**

```text
Circular Dependency Group:
{A, B, C}

Non-Cyclic Components:
{D}, {E}, {F}, {G}
```

**Condensation DAG**

```text
SCC 0 → SCC 1 → SCC 2 → SCC 3 → SCC 4
```

**Valid Execution Order**

```text
SCC 0 → SCC 1 → SCC 2 → SCC 3 → SCC 4
```

The modules inside SCC 0 must be treated as a single cyclic group. The remaining components can be processed after their dependencies have been satisfied.

The actual component numbering and order may vary depending on the graph traversal and implementation.

## 12. Time and Space Complexity

Let:

- V = Number of vertices (software modules).
- E = Number of edges (dependencies).

| Algorithm | Time Complexity |
|---|---|
| Graph Construction | O(V + E) |
| First DFS Traversal | O(V + E) |
| Graph Transpose | O(V + E) |
| Second DFS Traversal | O(V + E) |
| Kosaraju's Algorithm | O(V + E) |
| Condensation DAG Construction | O(V + E) |
| Kahn's Topological Sorting | O(V + E) |

**Overall Time Complexity:** O(V + E)

**Overall Space Complexity:** O(V + E)

The adjacency lists, transposed graph, DFS stack, visited arrays, SCC storage, and Condensation DAG require linear space relative to the number of vertices and edges.

## 13. Limitations

- Modules within the same circular dependency group cannot be independently ordered using topological sorting.
- The application identifies circular dependencies but does not automatically modify or resolve them.
- A valid topological order is not necessarily unique.
- The execution order depends on the dependency relationships in the uploaded dataset.
- Large dependency graphs may require more time and visual space to display clearly.

## 14. Future Scope

- Support additional dependency file formats.
- Allow users to interactively add or remove graph edges.
- Highlight individual dependency paths.
- Provide options to modify dependencies and compare the resulting graphs.
- Export circular dependency reports.
- Add larger datasets for testing graph performance.

## 15. Conclusion

CycleScope demonstrates the application of graph data structures and algorithms to software dependency analysis. Kosaraju's algorithm is used to identify Strongly Connected Components and detect circular dependencies. The resulting components are converted into a Condensation DAG, which is processed using Kahn's topological sorting algorithm to determine a valid execution order.

The interactive Streamlit interface makes the graph structure, algorithm stages, circular dependency groups, and execution sequence easier to understand.

The project combines theoretical graph concepts with a practical implementation in C++ and provides a visual way to explore how graph algorithms can be used to analyze software dependencies.