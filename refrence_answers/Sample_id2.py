import json


def sort_threads_by_cpu_last_accumulated(cpu_number):
    # Load data from file
    try:
        with open('../cpu_usage/cpu_usage_graph.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: cpu_usage_graph.json file not found.")
        return

    # Find the CPU node with the given cpu_number
    cpu_id = f"CPU_{cpu_number}"
    cpu_node = next((node for node in data['nodes'] if node.get('cpu_id') == str(cpu_number)), None)
    if not cpu_node:
        print(f"CPU {cpu_number} not found.")
        return

    # Create a mapping from thread node ID to thread_id
    thread_id_map = {}
    for node in data['nodes']:
        if node['entity'] == 'Thread':
            thread_id_map[node['id']] = node['thread_id']

    # Track the last accumulated time for each thread on the specified CPU
    thread_times = {}
    for link in data['links']:
        if link['relation'] == 'used_cpu' and link['target'] == cpu_id:
            thread_source = link['source']
            if thread_source in thread_id_map:
                thread_id = thread_id_map[thread_source]
                accumulated_times = link['accumulated_times']
                if accumulated_times:
                    # Directly use the last value
                    thread_times[thread_id] = accumulated_times[-1]

    # Sort the threads by the last accumulated time in descending order
    sorted_threads = sorted(thread_times.items(), key=lambda x: x[1], reverse=True)

    # Print the results
    print(f"Threads sorted by last accumulated time on CPU {cpu_number} (descending):")
    for thread_id, time_ns in sorted_threads:
        print(f"Thread {thread_id}: {time_ns} ns")


# Example usage:
cpu_number = 3  # Change this value to 0, 1, 2, or 3
sort_threads_by_cpu_last_accumulated(cpu_number)