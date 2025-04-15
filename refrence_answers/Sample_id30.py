import json

# Set the path to your JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"

# Define the target CPUs (IDs lower than 2) as a set
target_cpus = {"CPU_0", "CPU_1"}

# Load the JSON data
with open(json_file, "r") as f:
    graph_data = json.load(f)

links = graph_data.get("links", [])

# Build a mapping from thread to the set of CPUs it has used
thread_cpu_map = {}

for link in links:
    # Only consider links with the "used_cpu" relation.
    if link.get("relation") == "used_cpu":
        thread = link.get("source")
        cpu = link.get("target")
        if thread:
            if thread not in thread_cpu_map:
                thread_cpu_map[thread] = set()
            thread_cpu_map[thread].add(cpu)

# Find at least one thread that has run exclusively on the target CPUs.
# This means the set of CPUs for the thread must exactly equal target_cpus.
found_thread = None
for thread, cpus in thread_cpu_map.items():
    if cpus == target_cpus:
        found_thread = thread
        break

if found_thread:
    print(f"Thread {found_thread} has run exclusively on CPUs {target_cpus}.")
else:
    print(f"No thread has run exclusively on CPUs {target_cpus}.")
