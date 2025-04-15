import json

# Set the path to the JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"

# Load the JSON data
with open(json_file, "r") as f:
    data = json.load(f)

# Dictionary to hold peak accumulated times for each CPU.
# For each CPU (target), we will gather the peak accumulated time from each edge.
cpu_peaks = {}

# Iterate over each link (edge) with relation "used_cpu"
for link in data.get("links", []):
    if link.get("relation") != "used_cpu":
        continue
    cpu = link.get("target")
    if not cpu:
        continue
    # Extract accumulated times from the link (convert to float)
    times = []
    for t in link.get("accumulated_times", []):
        try:
            times.append(float(t))
        except Exception:
            continue
    if not times:
        continue
    # Use the maximum accumulated time for this edge as the thread's peak value on this CPU
    edge_peak = max(times)
    if cpu not in cpu_peaks:
        cpu_peaks[cpu] = []
    cpu_peaks[cpu].append(edge_peak)

# Now compute the difference between the maximum and minimum peak values for each CPU.
cpu_diff = {}
for cpu, peaks in cpu_peaks.items():
    if peaks:
        diff = max(peaks) - min(peaks)
        cpu_diff[cpu] = diff

# Identify the CPU with the lowest difference.
lowest_cpu = None
lowest_diff = None
for cpu, diff in cpu_diff.items():
    if lowest_diff is None or diff < lowest_diff:
        lowest_diff = diff
        lowest_cpu = cpu

# Print the fluctuation per CPU and the result.
print("Fluctuation (difference between highest and lowest accumulated times) per CPU:")
for cpu in sorted(cpu_diff):
    print(f"  {cpu}: {cpu_diff[cpu]:.0f} ns")

if lowest_cpu:
    print(f"\nCPU with the lowest fluctuation: {lowest_cpu} (difference = {lowest_diff:.0f} ns)")
else:
    print("No CPU data available to calculate fluctuation.")
