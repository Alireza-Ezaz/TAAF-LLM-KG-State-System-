import json

# -----------------------------
# Part 1: Count nodes and edges in the JSON file
# -----------------------------
json_file = "cpu_usage_graph.json"  # Adjust the path if needed

with open(json_file, "r") as f:
    graph_data = json.load(f)

# Extract nodes and edges lists
nodes = graph_data.get("nodes", [])
links = graph_data.get("links", [])

# Count nodes and edges
num_nodes = len(nodes)
num_edges = len(links)

print("Number of nodes:", num_nodes)
print("Number of edges:", num_edges)

# -----------------------------
# Part 2: Count lines in the text file
# -----------------------------
txt_file = "cpu_usage_input.txt"  # Adjust the path if needed

with open(txt_file, "r") as f:
    lines = f.readlines()

num_lines = len(lines)
print("Number of lines in the text file:", num_lines)
