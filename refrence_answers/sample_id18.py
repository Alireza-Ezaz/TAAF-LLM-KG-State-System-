import json
import math

# File path to your JSON data.
json_file = "../cpu_usage/cpu_usage_graph.json"

# Read the JSON data from the file.
with open(json_file, "r") as f:
    data = json.load(f)

# Get all nodes.
nodes = data.get("nodes", [])

# List to store busy times for CPUs in seconds (using integer division).
cpu_busy_seconds = []

# Iterate over nodes and extract busy_time_ns for CPU nodes.
for node in nodes:
    if node.get("entity") == "CPU":
        busy_ns = node.get("busy_time_ns")
        if busy_ns is not None:
            # Convert nanoseconds to seconds (discard the fractional part).
            busy_sec = busy_ns // 1000000000  # integer division
            cpu_busy_seconds.append(busy_sec)

# Proceed only if we found some CPU busy times.
if not cpu_busy_seconds:
    print("No CPU busy time data found.")
else:
    # Calculate the mean busy time.
    mean_busy = sum(cpu_busy_seconds) / len(cpu_busy_seconds)

    # Compute variance (population variance) using integer second values.
    variance = sum((x - mean_busy) ** 2 for x in cpu_busy_seconds) / len(cpu_busy_seconds)

    # Compute the standard deviation and discard any fractional part.
    std_dev = int(math.sqrt(variance))

    # Print out each CPU busy time in seconds and the computed standard deviation.
    print("CPU busy times (in seconds):")
    for node in nodes:
        if node.get("entity") == "CPU":
            busy_ns = node.get("busy_time_ns")
            if busy_ns is not None:
                busy_sec = busy_ns // 1000000000
                print(f"  {node.get('id')}: {busy_sec} s")

    print(f"\nStandard deviation of busy times across all CPUs: {std_dev} s")
