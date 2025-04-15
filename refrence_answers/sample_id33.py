import json

# Path to the JSON file containing the knowledge graph
file_path = "../cpu_usage/cpu_usage_graph.json"

# Load the JSON data
with open(file_path, "r") as f:
    data = json.load(f)

# Dictionary to group peak accumulated times per CPU.
# Key: CPU target (e.g., "CPU_0"), Value: list of peak accumulated times (floats)
cpu_times = {}

# Iterate over each link to extract accumulated times
for link in data.get("links", []):
    # Consider only links with the "used_cpu" relation
    if link.get("relation") != "used_cpu":
        continue

    target_cpu = link.get("target")
    if not target_cpu:
        continue

    # Extract numbers from the "accumulated_times" list
    times_list = []
    for t in link.get("accumulated_times", []):
        try:
            times_list.append(float(t))
        except Exception:
            continue

    if not times_list:
        continue

    # For a given edge (link) treat the peak as the maximum accumulated time
    edge_peak = max(times_list)
    if target_cpu not in cpu_times:
        cpu_times[target_cpu] = []
    cpu_times[target_cpu].append(edge_peak)

# Compute the difference (max minus min) of accumulated times for each CPU
cpu_diffs = {}
for cpu, times in cpu_times.items():
    if times:
        difference = max(times) - min(times)
        cpu_diffs[cpu] = difference
    else:
        cpu_diffs[cpu] = None

# Identify the CPU that has the greatest difference
max_cpu = None
max_diff = -1
for cpu, diff in cpu_diffs.items():
    if diff is not None and diff > max_diff:
        max_diff = diff
        max_cpu = cpu

# Print the differences for each CPU
print("Difference in peak accumulated times among threads per CPU:")
for cpu, diff in cpu_diffs.items():
    print(f"  {cpu}: difference = {diff:.0f} ns")

# Print which CPU has the greatest difference
if max_cpu:
    print(f"\nCPU with the greatest difference: {max_cpu} (difference = {max_diff:.0f} ns)")
else:
    print("No CPU data available.")
