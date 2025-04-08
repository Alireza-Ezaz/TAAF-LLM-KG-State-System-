import json


# Helper function to check if a value is numeric.
def is_numeric(val):
    # If the value is an int or float, it's numeric.
    if isinstance(val, (int, float)):
        return True
    # If it's a string, try converting it to a float.
    if isinstance(val, str):
        try:
            float(val)
            return True
        except ValueError:
            return False
    return False


# Name of the JSON file
json_file = "../cpu_usage/cpu_usage_graph.json"  # Adjust path as necessary

# Initialize variables to store the thread with the widest range.
widest_range = None
thread_with_widest_range = None
details_with_widest_range = None

# Read the JSON data from the file.
with open(json_file, "r") as f:
    data = json.load(f)

# Extract the list of link objects from the "links" key.
links = data.get("links", [])

# Iterate over each link to compute the range (max - min) of numeric times in time_per_occurrence.
for entry in links:
    # Get time_per_occurrence values
    times = entry.get("time_per_occurrence", [])

    # Extract numeric values
    numeric_times = []
    for time_item in times:
        if is_numeric(time_item):
            numeric_times.append(float(time_item))

    # We require at least two numeric values to have a meaningful range.
    if len(numeric_times) < 2:
        continue

    # Calculate the range: maximum minus minimum runtime.
    current_range = max(numeric_times) - min(numeric_times)

    # If this is the widest range encountered so far, store the details.
    if widest_range is None or current_range > widest_range:
        widest_range = current_range
        thread_with_widest_range = entry.get("source")
        details_with_widest_range = entry

# Output the result.
if thread_with_widest_range is not None:
    # Get all numeric values from time_per_occurrence for display
    numeric_values = []
    for val in details_with_widest_range.get("time_per_occurrence", []):
        if is_numeric(val):
            numeric_values.append(float(val))

    print("Thread with the widest range of runtime_per_occurrence:")
    print(f"  Source (Thread): {thread_with_widest_range}")
    print(f"  Target (CPU): {details_with_widest_range.get('target')}")
    print(f"  Range of runtime (ns): {widest_range}")
    print(f"  All numeric runtime_per_occurrence values: {', '.join(str(x) for x in numeric_values)}")
else:
    print("No thread with a numeric range in runtime_per_occurrence found.")
