import re
import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

# =============================================================================
# CONFIGURATION / OPTIONS
# =============================================================================
# Name of the input file containing the CPU usage analysis output.
input_filename = "cpu_usage_input.txt"
# Name of the output JSON file where the graph will be saved.
output_filename = "cpu_usage_graph.json"

# =============================================================================
# STEP 0: READ INPUT FROM TXT FILE
# =============================================================================
with open(input_filename, "r") as f:
    sample_output = f.read()


# =============================================================================
# STEP 1: PARSE THE OUTPUT FROM THE CPU USAGE ANALYSIS
# =============================================================================
def parse_cpu_usage_output(output_text):
    """
    Parses the CPU usage analysis output.
    Each line matching the pattern:
       "  CPUs/{cpu_id}/{thread_id} => {accumulated_cpu_time}"
    is converted into a record with keys:
      - 'cpu': CPU id (as string)
      - 'thread': thread id (as string)
      - 'accumulated_cpu_time': integer time in nanoseconds
    """
    records = []
    lines = output_text.strip().splitlines()
    pattern = re.compile(r"^\s+CPUs/(\d+)/(\S+)\s*=>\s*(\d+)")
    for line in lines:
        match = pattern.match(line)
        if match:
            cpu_id, thread_id, acc_time = match.groups()
            records.append({
                'cpu': cpu_id,
                'thread': thread_id,
                'accumulated_cpu_time': int(acc_time)
            })
    return records


records = parse_cpu_usage_output(sample_output)
print("Parsed Records:")
for rec in records:
    print(rec)

# =============================================================================
# STEP 2: AGGREGATE METRICS FOR CPU NODES AND (THREAD, CPU) EDGES
# =============================================================================

cpu_metrics = {}  # key: cpu id, value: dict with CPU properties
edge_metrics = {}  # key: (thread, cpu) tuple, value: dict with edge properties
thread_metrics = {}  # key: thread id, value: dict with accumulated_cpu_time and cpu_id

for rec in records:
    cpu = rec['cpu']
    thread = rec['thread']
    acc_time = rec['accumulated_cpu_time']

    if cpu not in cpu_metrics:
        cpu_metrics[cpu] = {'busy_time_ns': 0}
    cpu_metrics[cpu]['busy_time_ns'] += acc_time

    edge_key = (thread, cpu)
    if edge_key not in edge_metrics:
        edge_metrics[edge_key] = {
            'sum_accumulated_times_ns': 0,
            'edge_occurrence_count': 0,
            'accumulated_times': [],
            'time_per_occurrence': []
        }
    edge_metrics[edge_key]['accumulated_times'].append(acc_time)

    edge_metrics[edge_key]['edge_occurrence_count'] += 1

    # For each thread, store the maximum (latest) accumulated time and the cpu_id
    if thread not in thread_metrics or acc_time > thread_metrics[thread]['accumulated_time']:
        thread_metrics[thread] = {'cpu_id': cpu, 'accumulated_time': acc_time}
    else:
        # Keep the previous accumulated time if it's not the latest one.
        thread_metrics[thread]['accumulated_time'] = max(thread_metrics[thread]['accumulated_time'], acc_time)

# Compute additional CPU properties.
for cpu, metrics in cpu_metrics.items():
    unique_threads = {rec['thread'] for rec in records if rec['cpu'] == cpu}
    num_unique_threads = len(unique_threads)
    metrics['num_unique_threads'] = num_unique_threads
    if num_unique_threads > 0:
        metrics['avg_busy_time_per_thread_ns'] = metrics['busy_time_ns'] / num_unique_threads
    else:
        metrics['avg_busy_time_per_thread_ns'] = 0

    total_edge_occurrences = sum(em['edge_occurrence_count'] for (t, c), em in edge_metrics.items() if c == cpu)
    metrics['total_edge_occurrences'] = total_edge_occurrences

    max_avg_edge_time = 0
    for (t, c), em in edge_metrics.items():
        if c == cpu:
            avg_edge_time = em['sum_accumulated_times_ns'] / em['edge_occurrence_count']
            if avg_edge_time > max_avg_edge_time:
                max_avg_edge_time = avg_edge_time
    metrics['max_avg_edge_time_ns'] = max_avg_edge_time

# Calculate time used in each occurrence.
for (thread, cpu), em in edge_metrics.items():
    prev_time = None
    for time in em['accumulated_times']:
        if prev_time is None:
            em['time_per_occurrence'].append("N/A")
        else:
            em['time_per_occurrence'].append(time - prev_time)
        prev_time = time

# Calculate the new Average Accumulated Edge Time (ns).
for (thread, cpu), em in edge_metrics.items():
    # Average of accumulated times (sum of accumulated times divided by the number of occurrences)
    if em['edge_occurrence_count'] > 0:
        em['avg_accumulated_edge_time_ns'] = em['sum_accumulated_times_ns'] / em['edge_occurrence_count']
    else:
        em['avg_accumulated_edge_time_ns'] = 0

# =============================================================================
# STEP 3: BUILD THE KNOWLEDGE GRAPH (NETWORKX)
# =============================================================================
KG = nx.DiGraph()

# Add CPU nodes with the computed properties.
for cpu, metrics in cpu_metrics.items():
    node_id = f"CPU_{cpu}"
    KG.add_node(node_id,
                entity="CPU",
                cpu_id=cpu,
                busy_time_ns=metrics['busy_time_ns'],
                num_unique_threads=metrics['num_unique_threads'],
                avg_busy_time_per_thread_ns=metrics['avg_busy_time_per_thread_ns'],
                total_edge_occurrences=metrics['total_edge_occurrences'],
                max_avg_edge_time_ns=metrics['max_avg_edge_time_ns'])

# Add Thread nodes with only entity and thread_id.
for thread in thread_metrics:
    node_id = f"T_{thread}"
    KG.add_node(node_id,
                entity="Thread",
                thread_id=thread)  # Removed unnecessary fields

# Add edges from Threads to CPUs.
for (thread, cpu), em in edge_metrics.items():
    source = f"T_{thread}"
    target = f"CPU_{cpu}"

    # Update the edge metrics to use the last value from accumulated_times for sum_accumulated_times_ns
    sum_accumulated_times_ns = em['accumulated_times'][-1] if em['accumulated_times'] else 0

    # Filter out 'N/A' values from time_per_occurrence before calculating the average
    valid_time_per_occurrence = [time for time in em['time_per_occurrence'] if time != "N/A"]

    avg_time_per_occurrence = sum(valid_time_per_occurrence) / len(
        valid_time_per_occurrence) if valid_time_per_occurrence else 0

    KG.add_edge(source, target,
                relation="used_cpu",
                sum_accumulated_times_ns=sum_accumulated_times_ns,
                edge_occurrence_count=em['edge_occurrence_count'],
                avg_time_per_occurrence_ns=avg_time_per_occurrence,  # average of time per occurrence
                avg_accumulated_edge_time_ns=em['avg_accumulated_edge_time_ns'],  # new feature
                accumulated_times=em['accumulated_times'],  # Added accumulated_times
                time_per_occurrence=em['time_per_occurrence'])


# =============================================================================
# STEP 4: SAVE THE GRAPH TO A JSON FILE (Run this function on demand)
# =============================================================================
def save_graph_json(graph, filename):
    """
    Converts the given NetworkX graph to node-link data format and saves it to a JSON file.
    """
    graph_data = json_graph.node_link_data(graph)
    with open(filename, "w") as json_file:
        json.dump(graph_data, json_file, indent=4)
    print(f"Knowledge graph saved to '{filename}'.")


# The following call is commented out so that the graph is not saved every time.
# Uncomment the next line when you want to save the graph.
save_graph_json(KG, output_filename)

# =============================================================================
# STEP 5: PRINT METRICS AND VISUALIZE THE KNOWLEDGE GRAPH
# =============================================================================
print("\n=== CPU Metrics (All Threads Treated Equally) ===")
for cpu, metrics in cpu_metrics.items():
    print(f"CPU {cpu}:")
    print(f"  Busy Time (ns): {metrics['busy_time_ns']}")
    print(f"  Number of Unique Threads: {metrics['num_unique_threads']}")
    print(f"  Avg Busy Time per Thread (ns): {metrics['avg_busy_time_per_thread_ns']:.2f}")
    print(f"  Total Edge Occurrences: {metrics['total_edge_occurrences']}")
    print(f"  Max Avg Edge Time (ns): {metrics['max_avg_edge_time_ns']:.2f}")

print("\n=== Thread Metrics ===")
for thread in thread_metrics:
    print(f"Thread {thread}")

print("\n=== Edge Metrics (Thread -> CPU) ===")
for (thread, cpu), em in edge_metrics.items():
    valid_time_per_occurrence = [time for time in em['time_per_occurrence'] if time != "N/A"]
    avg_time_per_occurrence = sum(valid_time_per_occurrence) / len(
        valid_time_per_occurrence) if valid_time_per_occurrence else 0
    print(f"Thread {thread} -> CPU {cpu}:")
    print(f"  Total Edge Time (ns): {em['sum_accumulated_times_ns']}")
    print(f"  Edge Occurrence Count: {em['edge_occurrence_count']}")
    print(f"  Average Time per Occurrence (ns): {avg_time_per_occurrence}")
    print(f"  Average Accumulated Edge Time (ns): {em['avg_accumulated_edge_time_ns']}")
    print(f"  Accumulated Times: {em['accumulated_times']}")
    print(f"  Time per Occurrence: {em['time_per_occurrence']}")

# Visualize the Knowledge Graph.
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(KG, k=0.5)
node_colors = []
for node in KG.nodes(data=True):
    if node[1]['entity'] == "CPU":
        node_colors.append('red')
    elif node[1]['entity'] == "Thread":
        node_colors.append('green')
    else:
        node_colors.append('grey')
nx.draw(KG, pos, with_labels=True, node_color=node_colors, node_size=1500, arrowsize=20)
plt.title("Knowledge Graph from CPU Usage Analysis (All Threads Treated Equally)")
plt.show()
