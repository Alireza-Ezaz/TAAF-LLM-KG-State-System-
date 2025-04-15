import json

# Path to the JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"

# Load the JSON data from the file
with open(json_file, "r") as f:
    data = json.load(f)

# Build a list of available CPUs from the nodes section (nodes with entity "CPU")
available_cpus = {node["id"] for node in data.get("nodes", []) if node.get("entity") == "CPU"}

# Build a mapping from thread (source) to set of CPUs (target) in links (edges)
thread_to_cpus = {}

# Iterate over each link with relation "used_cpu"
for link in data.get("links", []):
    if link.get("relation") == "used_cpu":
        thread = link.get("source")
        cpu = link.get("target")
        if thread and cpu:
            thread_to_cpus.setdefault(thread, set()).add(cpu)

# Print results: for each thread, list the CPUs it was scheduled on at least once.
print("Mapping of Threads to the CPUs they ran on (at least once):\n")
for thread, cpus in thread_to_cpus.items():
    print(f"  {thread}: {sorted(cpus)}")

# --- Counter examples ---
# For instance, here we print the threads that did NOT run on every available CPU.
print("\nCounter examples: Threads that did not run on all available CPUs")
print(f"Available CPU nodes: {sorted(available_cpus)}")
not_full_schedule = {thread: cpus for thread, cpus in thread_to_cpus.items()
                     if cpus != available_cpus}
if not_full_schedule:
    for thread, cpus in not_full_schedule.items():
        missing = available_cpus - cpus
        print(f"  {thread} ran on {sorted(cpus)} but never ran on {sorted(missing)}")
else:
    print("  All threads appear to have run on every available CPU node.")

# Also, mention threads that never appeared in any link (if any)
# We obtain all threads from nodes with entity "Thread"
all_thread_nodes = {node["id"] for node in data.get("nodes", []) if node.get("entity") == "Thread"}
threads_without_any_cpu = all_thread_nodes - set(thread_to_cpus.keys())
if threads_without_any_cpu:
    print("\nThreads present in the graph that never have been scheduled on any CPU:")
    for thread in sorted(threads_without_any_cpu):
        print(f"  {thread}")
else:
    print("\nEvery thread node has at least one scheduling record in the links.")
