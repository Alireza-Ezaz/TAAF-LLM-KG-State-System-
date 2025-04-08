import json

# Name of the JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"

# Initialize counter for threads with peak accumulated time > 1e9 ns
count_threads = 0

# Read the JSON data from the file.
with open(json_file, "r") as f:
    data = json.load(f)

# Extract the list of link objects from the "links" key.
links = data.get("links", [])

# Iterate over each link
for entry in links:
    # Check if the entry is associated with "CPU_2"
    if entry.get("target") == "CPU_0":
        # Get the list of accumulated times
        acc_times = entry.get("accumulated_times", [])
        if not acc_times:
            continue  # Skip if no accumulated times are present

        # Compute the peak (maximum) accumulated time in this entry.
        peak_time = max(acc_times)

        # If the peak accumulated time exceeds 1e9 ns, increment the count.
        if peak_time > 1e8:
            count_threads += 1
            print(f"Thread ID: {entry['source']}, Peak Accumulated Time: {peak_time} ns")

print(f"Number of threads with a peak accumulated time > 1e8 ns on CPU 0: {count_threads}")
