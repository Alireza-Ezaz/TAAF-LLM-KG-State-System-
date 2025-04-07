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
#
# We treat every record (including those with thread "0") equally.
#
# For each CPU, we calculate:
#   - busy_time_ns: total accumulated CPU time (sum of all records) on that CPU.
#
# For each (thread, CPU) pair (edge), we record:
#   - total_edge_time_ns: sum of accumulated times for that (thread, CPU) pair.
#   - edge_occurrence_count: number of records for that pair.
#   - avg_edge_time_ns: average time per record on that edge.
#
# Additionally, for each CPU we derive:
#   - num_unique_threads: number of unique threads running on that CPU.
#   - avg_busy_time_per_thread_ns: busy_time_ns divided by num_unique_threads.
#   - total_edge_occurrences: total number of (thread, CPU) occurrences on that CPU.
#   - max_avg_edge_time_ns: maximum average edge time among all edges on that CPU.
cpu_metrics = {}  # key: cpu id, value: dict with CPU properties
edge_metrics = {}  # key: (thread, cpu) tuple, value: dict with edge properties
thread_metrics = {}  # key: thread id, value: latest accumulated_cpu_time

for rec in records:
    cpu = rec['cpu']
    thread = rec['thread']
    acc_time = rec['accumulated_cpu_time']

    if cpu not in cpu_metrics:
        cpu_metrics[cpu] = {'busy_time_ns': 0}
    # Add the record's time to the CPU's busy time.
    cpu_metrics[cpu]['busy_time_ns'] += acc_time

    # Update edge metrics for each (thread, CPU) pair.
    edge_key = (thread, cpu)
    if edge_key not in edge_metrics:
        edge_metrics[edge_key] = {
            'total_edge_time_ns': 0,
            'edge_occurrence_count': 0,
            'accumulated_times': []
        }
    edge_metrics[edge_key]['total_edge_time_ns'] += acc_time
    edge_metrics[edge_key]['edge_occurrence_count'] += 1
    edge_metrics[edge_key]['accumulated_times'].append(acc_time)

    # For each thread, store the maximum (latest) accumulated time.
    if thread not in thread_metrics or acc_time > thread_metrics[thread]:
        thread_metrics[thread] = acc_time

# Compute additional CPU properties.
for cpu, metrics in cpu_metrics.items():
    # Unique threads on this CPU.
    unique_threads = {rec['thread'] for rec in records if rec['cpu'] == cpu}
    num_unique_threads = len(unique_threads)
    metrics['num_unique_threads'] = num_unique_threads
    if num_unique_threads > 0:
        metrics['avg_busy_time_per_thread_ns'] = metrics['busy_time_ns'] / num_unique_threads
    else:
        metrics['avg_busy_time_per_thread_ns'] = 0

    # Total edge occurrences for this CPU.
    total_edge_occurrences = sum(em['edge_occurrence_count'] for (t, c), em in edge_metrics.items() if c == cpu)
    metrics['total_edge_occurrences'] = total_edge_occurrences

    # Maximum average edge time among all edges on this CPU.
    max_avg_edge_time = 0
    for (t, c), em in edge_metrics.items():
        if c == cpu:
            avg_edge_time = em['total_edge_time_ns'] / em['edge_occurrence_count']
            if avg_edge_time > max_avg_edge_time:
                max_avg_edge_time = avg_edge_time
    metrics['max_avg_edge_time_ns'] = max_avg_edge_time

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

# Add Thread nodes.
for thread, latest_time in thread_metrics.items():
    node_id = f"T_{thread}"
    KG.add_node(node_id,
                entity="Thread",
                thread_id=thread,
                latest_accumulated_time_ns=latest_time)

# Add edges from Threads to CPUs.
for (thread, cpu), em in edge_metrics.items():
    source = f"T_{thread}"
    target = f"CPU_{cpu}"
    avg_edge_time = em['total_edge_time_ns'] / em['edge_occurrence_count']
    KG.add_edge(source, target,
                relation="used_cpu",
                total_edge_time_ns=em['total_edge_time_ns'],
                edge_occurrence_count=em['edge_occurrence_count'],
                avg_edge_time_ns=avg_edge_time,
                accumulated_times=em['accumulated_times'])


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
# save_graph_json(KG, output_filename)

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
for thread, latest_time in thread_metrics.items():
    print(f"Thread {thread}: Latest Accumulated Time (ns) = {latest_time}")

print("\n=== Edge Metrics (Thread -> CPU) ===")
for (thread, cpu), em in edge_metrics.items():
    avg_edge_time = em['total_edge_time_ns'] / em['edge_occurrence_count']
    print(f"Thread {thread} -> CPU {cpu}:")
    print(f"  Total Edge Time (ns): {em['total_edge_time_ns']}")
    print(f"  Edge Occurrence Count: {em['edge_occurrence_count']}")
    print(f"  Average Edge Time (ns): {avg_edge_time:.2f}")
    print(f"  Recorded Values: {em['accumulated_times']}")

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
