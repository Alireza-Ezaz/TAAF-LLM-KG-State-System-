import json

# Name of the JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"

# Initialize variables to hold the maximum runtime and corresponding entry.
max_runtime = None
max_entry = None

# Read the JSON data from the file.
with open(json_file, "r") as f:
    data = json.load(f)

# Assume that the JSON has a "links" key that holds an array of relation objects.
links = data.get("links", [])

# Iterate over each link entry.
for entry in links:
    # Each entry has a list for "time_per_occurrence".
    for time_str in entry.get("time_per_occurrence", []):
        try:
            runtime = float(time_str)
        except ValueError:
            # Skip non-numeric values like "N/A".
            continue

        # Update maximum runtime if this runtime is larger than the current max.
        if max_runtime is None or runtime > max_runtime:
            max_runtime = runtime
            max_entry = entry

# Report the results.
if max_entry is not None:
    print("Thread with the longest individual runtime:")
    print(f"  Source (Thread): {max_entry['source']}")
    print(f"  Target (CPU): {max_entry['target']}")
    print(f"  Max Individual Runtime (ns): {max_runtime}")
else:
    print("No valid numeric runtime values found in the data.")
