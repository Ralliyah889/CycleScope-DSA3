CXX = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
INCLUDES = -Isrc

SRC = src/graph.cpp src/kosaraju.cpp src/condensation.cpp src/topological_sort.cpp
MAIN = src/main.cpp
TEST_SRC = tests/test_cpp.cpp

BIN_DIR = bin
TARGET = $(BIN_DIR)/dependency_analyzer
TEST_TARGET = $(BIN_DIR)/test_cpp

.PHONY: all clean test run_tests

all: $(TARGET)

$(TARGET): $(SRC) $(MAIN)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC) $(MAIN) -o $(TARGET)
	@echo "Build successful: $(TARGET)"

$(TEST_TARGET): $(SRC) $(TEST_SRC)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC) $(TEST_SRC) -o $(TEST_TARGET)
	@echo "Build test executable successful: $(TEST_TARGET)"

test: $(TEST_TARGET)
	@echo "Running C++ algorithm tests..."
	./$(TEST_TARGET)

clean:
	rm -rf $(BIN_DIR)
