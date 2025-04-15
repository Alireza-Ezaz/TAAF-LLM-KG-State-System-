import json

# Define file path and the threshold value (1e6 ns)
file_path = "../cpu_usage/cpu_usage_graph.json"
peak_threshold = 1e6  # 1,000,000 ns

# Load the JSON data from the file
with open(file_path, "r") as f:
    data = json.load(f)

# Dictionary to store threads (using the "source" field) and their peak accumulated time on CPU_2
threads_peak = {}

# Iterate over each link in the JSON data
for link in data.get("links", []):
    # Only consider edges for CPU_2
    if link.get("target") == "CPU_2":
        thread = link.get("source")
        # Get the accumulated_times list from the edge
        times = link.get("accumulated_times", [])
        numeric_times = []
        # Convert each value in the list to a float (if possible)
        for t in times:
            if isinstance(t, (int, float)):
                numeric_times.append(t)
            else:
                try:
                    numeric_times.append(float(t))
                except Exception:
                    continue
        if numeric_times:
            peak = max(numeric_times)
            # Check if the peak exceeds the threshold
            if peak > peak_threshold:
                # Store or update the peak accumulated time for the thread
                threads_peak[thread] = max(threads_peak.get(thread, 0), peak)

# Display the results
if threads_peak:
    print("Threads on CPU_2 with a peak accumulated time > 1e6 ns:")
    for thread, peak in threads_peak.items():
        print(f"  {thread}: Peak Accumulated Time = {peak} ns")
    print(f"Total number of threads: {len(threads_peak)}")
else:
    print("No threads on CPU_2 have a peak accumulated time > 1e6 ns.")
