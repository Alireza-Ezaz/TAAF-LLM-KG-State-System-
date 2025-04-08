import json

# Name of the JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"

# Initialize a counter for total runs (edge_occurrence_count) on CPU 1 for threads that ran more than once.
threads_count = 0

# Dictionary to store thread names and their total occurrence counts.
thread_details = {}

# Read the JSON data from the file.
with open(json_file, "r") as f:
    data = json.load(f)

# Extract the list of link objects from the "links" key.
links = data.get("links", [])

# Iterate over each link to find those for CPU 1 that have been run more than once.
for entry in links:
    # Check if the target is "CPU_1" and the edge_occurrence_count is greater than 1.
    if entry.get("target") == "CPU_2" and entry.get("edge_occurrence_count", 0) > 1:
        # Add the occurrence count to the global counter
        edge_occ_count = entry.get("edge_occurrence_count", 0)
        threads_count += edge_occ_count

        # Get the thread name from the "source" field.
        thread_name = entry.get("source")

        # If the thread is already in our dictionary, add the count,
        # otherwise, initialize it.
        if thread_name in thread_details:
            thread_details[thread_name] += edge_occ_count
        else:
            thread_details[thread_name] = edge_occ_count

# Print the aggregated result and the list of thread names with their occurrence counts.
print(f"Total number of runs (edge_occurrence_count) for threads on CPU 2 that ran more than once: {threads_count}")
print("\nThread names and their occurrence counts on CPU 2:")
for thread, count in thread_details.items():
    print(f"  {thread}: {count}")
