import json

# File path to the JSON file
file_path = "../cpu_usage/cpu_usage_graph.json"

# Load the JSON data from the file.
with open(file_path, "r") as f:
    data = json.load(f)

# Dictionary to group peak accumulated times per CPU.
# We consider only links with "used_cpu" relation.
cpu_times = {}

for link in data.get("links", []):
    if link.get("relation") != "used_cpu":
        continue

    cpu = link.get("target")
    if not cpu:
        continue

    # Convert accumulated_times values to floats
    values = []
    for v in link.get("accumulated_times", []):
        try:
            values.append(float(v))
        except Exception:
            continue
    if not values:
        continue

    # For each link, use the maximum accumulated value as the thread's peak.
    peak = max(values)
    if cpu not in cpu_times:
        cpu_times[cpu] = []
    cpu_times[cpu].append(peak)

# Compute fluctuation (difference between the max and min peak) for each CPU.
cpu_fluctuations = {}
for cpu, peaks in cpu_times.items():
    if peaks:
        fluctuation = max(peaks) - min(peaks)
        cpu_fluctuations[cpu] = fluctuation

# Find the CPU with the highest fluctuation.
max_cpu = None
max_diff = -1
for cpu, diff in cpu_fluctuations.items():
    if diff > max_diff:
        max_diff = diff
        max_cpu = cpu

# Mapping to the provided answer choices.
answer_map = {
    "CPU_0": "A. CPU_0",
    "CPU_1": "B. CPU_1",
    "CPU_2": "C. CPU_2",
    "CPU_3": "D. CPU_3"
}

print("Fluctuation of peak accumulated times by CPU (in ns):")
for cpu in sorted(cpu_fluctuations.keys()):
    print(f"  {cpu}: {cpu_fluctuations[cpu]:.0f} ns")

if max_cpu:
    print(f"\nAnswer: {answer_map.get(max_cpu, max_cpu)} (highest fluctuation = {max_diff:.0f} ns)")
else:
    print("No data available to determine fluctuations.")
