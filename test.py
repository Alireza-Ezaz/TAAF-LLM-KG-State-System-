import re
import networkx as nx
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURATION / OPTIONS
# =============================================================================
# Define the interval length (in nanoseconds) used for the query.
INTERVAL_LENGTH_NS = 1_000_000_000  # 1 second

# Sample output from your Trace Compass CPU usage analysis.
# Each line is expected to be in the format:
#   "  CPUs/{cpu_id}/{thread_id} => {accumulated_cpu_time}"
sample_output = """
  CPUs/2/5235 => 885106
  CPUs/1/0 => 600228811
  CPUs/1/5130 => 34468172
  CPUs/2/17 => 46882
  CPUs/0/9 => 90232
  CPUs/3/22 => 88488
  CPUs/2/5130 => 12974809
  CPUs/2/18 => 590354
  CPUs/3/23 => 144482
  CPUs/1/12 => 67536
  CPUs/3/5130 => 18459740
  CPUs/1/7 => 48863
  CPUs/0/5130 => 4457969
  CPUs/2/5125 => 266934
  CPUs/0/5119 => 176098
  CPUs/0/2186 => 23622189
  CPUs/3/5123 => 390566
  CPUs/1/5124 => 79031
  CPUs/2/5124 => 376275
  CPUs/3/5125 => 46419
  CPUs/2/5126 => 107474
  CPUs/1/5125 => 520813
  CPUs/3/5127 => 35811
  CPUs/1/5127 => 348498
  CPUs/3/5129 => 31052
  CPUs/1/5129 => 434990
  CPUs/3/5128 => 183827
  CPUs/1/5132 => 28659
  CPUs/2/5132 => 348981
  CPUs/1/5131 => 605137
  CPUs/1/4740 => 5572
  CPUs/3/2208 => 314978
  CPUs/2/2208 => 3925379
  CPUs/2/5133 => 125183
  CPUs/0/5134 => 34616
  CPUs/1/5134 => 2271105
  CPUs/3/5133 => 653455
  CPUs/2/5135 => 40602
  CPUs/0/5136 => 51641
  CPUs/0/5137 => 33432
  CPUs/1/5136 => 1914795
  CPUs/1/5137 => 486419
  CPUs/3/5135 => 649248
  CPUs/2/5138 => 99310
  CPUs/0/5139 => 35320
  CPUs/1/5139 => 1875427
  CPUs/3/5138 => 581983
  CPUs/3/5140 => 90093
  CPUs/1/5141 => 33480
  CPUs/3/5141 => 1929751
  CPUs/0/5140 => 626548
  CPUs/2/5142 => 40778
  CPUs/0/5143 => 33175
  CPUs/1/5143 => 3497276
  CPUs/3/5142 => 586939
  CPUs/3/5144 => 37013
  CPUs/1/5145 => 46551
  CPUs/2/5145 => 3078761
  CPUs/0/5144 => 617644
  CPUs/0/5146 => 37798
  CPUs/3/5147 => 32822
  CPUs/0/5147 => 3279252
  CPUs/1/5146 => 559416
  CPUs/0/5148 => 35820
  CPUs/3/5149 => 36798
  CPUs/0/5149 => 3318160
  CPUs/1/5148 => 606192
  CPUs/0/5150 => 34144
  CPUs/3/5151 => 39954
  CPUs/0/5151 => 3134218
  CPUs/1/5150 => 623573
  CPUs/0/5152 => 49958
  CPUs/3/5153 => 37466
  CPUs/0/5153 => 3111696
  CPUs/1/5152 => 620413
  CPUs/0/5154 => 37397
  CPUs/3/5155 => 32918
  CPUs/0/5155 => 3071499
  CPUs/1/5154 => 559050
  CPUs/0/5156 => 40052
  CPUs/3/5157 => 3065248
  CPUs/1/5156 => 605366
  CPUs/1/5158 => 39938
  CPUs/1/5159 => 3134108
  CPUs/0/5158 => 609677
  CPUs/0/5160 => 38546
  CPUs/0/5161 => 3138102
  CPUs/1/5160 => 561921
  CPUs/3/5162 => 36731
  CPUs/1/5163 => 36978
  CPUs/3/5163 => 3053660
  CPUs/0/5162 => 644749
  CPUs/0/5164 => 35943
  CPUs/0/5165 => 3142009
  CPUs/1/5164 => 556081
  CPUs/3/5166 => 35718
  CPUs/1/5167 => 38909
  CPUs/2/5167 => 3088980
  CPUs/0/5166 => 580496
  CPUs/0/5168 => 36279
  CPUs/1/5168 => 486200
  CPUs/0/5169 => 44312
  CPUs/1/5169 => 3133180
  CPUs/2/5168 => 77101
  CPUs/0/5170 => 37710
  CPUs/3/5171 => 37554
  CPUs/0/5171 => 3316273
  CPUs/1/5170 => 567240
  CPUs/0/5173 => 28287
  CPUs/1/5173 => 3185199
  CPUs/0/5172 => 670117
  CPUs/1/5175 => 29982
  CPUs/2/5175 => 3113946
  CPUs/1/5174 => 627484
  CPUs/2/5176 => 35679
  CPUs/3/5177 => 29865
  CPUs/2/5177 => 3126266
  CPUs/3/5176 => 622617
  CPUs/2/5179 => 30662
  CPUs/0/5179 => 3151394
  CPUs/2/5178 => 632963
  CPUs/0/5181 => 27728
  CPUs/1/5181 => 516339
  CPUs/0/5180 => 610821
  CPUs/1/5183 => 29440
  CPUs/3/5183 => 644073
  CPUs/1/5182 => 671254
  CPUs/3/5184 => 40339
  CPUs/2/5185 => 30439
  CPUs/3/5185 => 528471
  CPUs/2/5184 => 635582
  CPUs/1/5186 => 38131
  CPUs/3/5187 => 22892
  CPUs/1/5187 => 544858
  CPUs/3/5186 => 580865
  CPUs/1/5189 => 26189
  CPUs/0/5189 => 565478
  CPUs/1/5188 => 650329
  CPUs/0/5191 => 29305
  CPUs/3/5191 => 3361903
  CPUs/0/5190 => 669806
  CPUs/0/5193 => 31388
  CPUs/2/5193 => 3266679
  CPUs/0/5192 => 706418
  CPUs/1/5195 => 26949
  CPUs/3/5195 => 3168657
  CPUs/1/5194 => 620366
  CPUs/3/5197 => 29859
  CPUs/2/5197 => 3122474
  CPUs/3/5196 => 594453
  CPUs/2/5199 => 30250
  CPUs/0/5199 => 3223257
  CPUs/2/5198 => 616583
  CPUs/0/5201 => 33898
  CPUs/1/5201 => 3236259
  CPUs/0/5200 => 660715
  CPUs/3/5203 => 29878
  CPUs/1/5203 => 3196488
  CPUs/3/5202 => 638266
  CPUs/1/5205 => 30311
  CPUs/2/5205 => 3146569
  CPUs/1/5204 => 648560
  CPUs/2/5207 => 26662
  CPUs/3/5207 => 3145743
  CPUs/2/5206 => 582691
  CPUs/3/5208 => 37675
  CPUs/0/5209 => 26165
  CPUs/3/5209 => 3023434
  CPUs/0/5208 => 621627
  CPUs/3/5211 => 27302
  CPUs/1/5211 => 3139699
  CPUs/3/5210 => 588964
  CPUs/1/5213 => 27844
  CPUs/2/5213 => 3143275
  CPUs/1/5212 => 574458
  CPUs/1/5215 => 27447
  CPUs/3/5215 => 3065312
  CPUs/1/5214 => 598009
  CPUs/3/5217 => 26704
  CPUs/0/5217 => 3134776
  CPUs/3/5216 => 560809
  CPUs/3/5219 => 26335
  CPUs/0/5219 => 3087578
  CPUs/3/5218 => 571988
  CPUs/0/5221 => 26826
  CPUs/2/5221 => 3054326
  CPUs/0/5220 => 624951
  CPUs/2/5223 => 25437
  CPUs/0/5223 => 3064008
  CPUs/2/5222 => 575195
  CPUs/0/5225 => 25690
  CPUs/1/5225 => 3064070
  CPUs/0/5224 => 584197
  CPUs/1/5227 => 26653
  CPUs/2/5227 => 3060369
  CPUs/1/5226 => 568872
  CPUs/2/5229 => 28741
  CPUs/0/5229 => 534161
  CPUs/2/5228 => 623845
  CPUs/0/5230 => 41647
  CPUs/3/5231 => 26325
  CPUs/0/5231 => 575635
  CPUs/3/5230 => 625676
  CPUs/2/5232 => 37313
  CPUs/0/5233 => 23478
  CPUs/2/5233 => 799671
  CPUs/1/5234 => 71739
  CPUs/2/5234 => 697691
  CPUs/3/5233 => 131858
  CPUs/0/5232 => 556112
  CPUs/2/5236 => 24368
  CPUs/2/4740 => 14903
  CPUs/0/1 => 103229
  CPUs/3/351 => 67883
  CPUs/2/351 => 43596
  CPUs/2/193 => 71752
  CPUs/0/508 => 64035
  CPUs/3/466 => 29607
  CPUs/0/0 => 14586730288
  CPUs/0/15322 => 988088
  CPUs/3/0 => 14545717632
  CPUs/3/4740 => 23126252
  CPUs/3/0 => 14877711877
  CPUs/0/0 => 14726729809
  CPUs/3/507 => 182777
  CPUs/2/0 => 14316925902
  CPUs/0/193 => 336633
  CPUs/3/0 => 14880022294
  CPUs/3/154 => 224758
  CPUs/3/0 => 14880078016
  CPUs/2/508 => 290208
  CPUs/3/154 => 228978
  CPUs/2/0 => 14904969181
  CPUs/2/129 => 183279
  CPUs/2/154 => 117862
  CPUs/2/0 => 14907155004
  CPUs/2/129 => 185899
  CPUs/2/0 => 14909445810
  CPUs/2/129 => 188173
  CPUs/2/0 => 14909489775
  CPUs/2/129 => 190370
  CPUs/2/154 => 129851
  CPUs/3/0 => 14880080127
  CPUs/3/4740 => 28818231
  CPUs/3/0 => 14887917588
  CPUs/0/0 => 14878741242
  CPUs/3/507 => 226092
  CPUs/2/0 => 14911694587
  CPUs/0/193 => 404709
  CPUs/2/508 => 368799
  CPUs/0/0 => 14894671510
  CPUs/0/15322 => 991494
  CPUs/3/0 => 14890342519
  CPUs/3/2559 => 350972
  CPUs/3/0 => 14958322544
  CPUs/3/2559 => 353672
  CPUs/0/0 => 14926620585
  CPUs/0/4740 => 37233
  CPUs/1/5236 => 13692921914
  CPUs/1/5096 => 440875
  CPUs/2/0 => 14920851355
  CPUs/2/11873 => 234217
  CPUs/0/0 => 14978615921
  CPUs/0/15322 => 995122
  CPUs/2/0 => 15012769774
  CPUs/2/11873 => 239586
  CPUs/0/0 => 15002612645
  CPUs/0/15322 => 1019724
  CPUs/0/0 => 15126587898
  CPUs/0/193 => 443828
  CPUs/1/5236 => 14388909318
  CPUs/1/5096 => 444380
  CPUs/1/5236 => 14544905045
  CPUs/1/5096 => 451264
  CPUs/0/0 => 15131970752
  CPUs/0/15322 => 1023237
  CPUs/0/0 => 15326571084
  CPUs/0/510 => 965603
  CPUs/0/0 => 15369347427
  CPUs/0/510 => 1001728
  CPUs/0/0 => 15369548124
  CPUs/0/510 => 1083098
  CPUs/0/0 => 15387832701
  CPUs/0/510 => 1109737
  CPUs/0/0 => 15441821949
  CPUs/0/510 => 1137041
  CPUs/0/0 => 15469885809
  CPUs/0/15322 => 1026735
  CPUs/0/0 => 15526381889
  CPUs/0/15322 => 1030195
  CPUs/0/510 => 1151208
  CPUs/0/7 => 253766
  CPUs/2/0 => 15108798517
  CPUs/2/11873 => 252422
  CPUs/0/4740 => 40393
  CPUs/1/5236 => 14545700844
  CPUs/1/5096 => 453482
  CPUs/3/0 => 14962317412
  CPUs/3/577 => 117980
  CPUs/3/2559 => 361376
  CPUs/0/3 => 508243
  CPUs/1/11 => 20740
  CPUs/2/16 => 10360
  CPUs/3/21 => 10600
  CPUs/0/10 => 9687
  CPUs/3/530 => 156473
  CPUs/3/7 => 118875
  CPUs/3/4740 => 34404252
  CPUs/3/507 => 236919
  CPUs/0/193 => 456832
  CPUs/3/154 => 284692
  CPUs/2/508 => 411976
  CPUs/2/129 => 192601
  CPUs/2/154 => 136627
  CPUs/2/7 => 456775
  CPUs/1/13 => 228525
"""


# =============================================================================
# STEP 1: PARSE THE OUTPUT FROM THE CPU USAGE ANALYSIS
# =============================================================================
def parse_cpu_usage_output(output_text):
    """
    Parses the CPU usage analysis output.
    Each relevant line should match the pattern:
       "  CPUs/{cpu_id}/{thread_id} => {accumulated_cpu_time}"
    Returns a list of records with:
       'cpu': CPU id (str)
       'thread': thread id (str)
       'accumulated_cpu_time': integer (nanoseconds)
    """
    records = []
    lines = output_text.strip().splitlines()
    pattern = re.compile(r"^\s+CPUs/(\d+)/(\S+)\s*=>\s*(\d+)")
    for line in lines:
        match = pattern.match(line)
        if match:
            cpu_id, thread_id, acc_time = match.groups()
            record = {
                'cpu': cpu_id,
                'thread': thread_id,
                'accumulated_cpu_time': int(acc_time)
            }
            records.append(record)
    return records


records = parse_cpu_usage_output(sample_output)
print("Parsed Records:")
for rec in records:
    print(rec)

# =============================================================================
# STEP 2: AGGREGATE METRICS FOR CPU NODES AND THREAD-CPU EDGES
# =============================================================================
#
# For each record:
#   - If thread=="0", treat as idle time.
#   - Otherwise, treat as busy time.
# We accumulate:
#   - For each CPU: total, idle, busy times and compute utilization.
#   - For each (thread, cpu) edge: sum accumulated_cpu_time, count occurrences, and store each value.
#   - For each Thread: the latest (largest) accumulated_cpu_time.
#
cpu_metrics = {}  # key: cpu id, value: dict with 'total', 'idle', 'busy'
edge_metrics = {}  # key: (thread, cpu) tuple, value: dict with 'total_time', 'count', 'accumulated_times'
thread_metrics = {}  # key: thread id, value: latest accumulated_cpu_time

for rec in records:
    cpu = rec['cpu']
    thread = rec['thread']
    acc_time = rec['accumulated_cpu_time']

    if cpu not in cpu_metrics:
        cpu_metrics[cpu] = {'total': 0, 'idle': 0, 'busy': 0}
    cpu_metrics[cpu]['total'] += acc_time
    if thread == "0":
        cpu_metrics[cpu]['idle'] += acc_time
    else:
        cpu_metrics[cpu]['busy'] += acc_time
        edge_key = (thread, cpu)
        if edge_key not in edge_metrics:
            edge_metrics[edge_key] = {'total_time': 0, 'count': 0, 'accumulated_times': []}
        edge_metrics[edge_key]['total_time'] += acc_time
        edge_metrics[edge_key]['count'] += 1
        edge_metrics[edge_key]['accumulated_times'].append(acc_time)
        # For thread metrics, we consider the highest (latest) accumulated value
        if thread not in thread_metrics or acc_time > thread_metrics[thread]:
            thread_metrics[thread] = acc_time

# Compute utilization for each CPU node.
for cpu, metrics in cpu_metrics.items():
    busy = metrics['busy']
    utilization = (busy / INTERVAL_LENGTH_NS) * 100  # as percentage
    metrics['utilization'] = utilization

# =============================================================================
# STEP 3: BUILD THE KNOWLEDGE GRAPH (NETWORKX)
# =============================================================================
#
# Create nodes for CPUs and Threads.
# For CPU nodes: attach metrics (total, idle, busy, utilization).
# For Thread nodes: attach overall (latest) accumulated CPU time.
# For each edge from a Thread to a CPU, attach:
#   - total accumulated CPU time, count, average, and list of individual accumulated times.
#
KG = nx.DiGraph()

# Add CPU nodes.
for cpu, metrics in cpu_metrics.items():
    node_id = f"CPU_{cpu}"
    KG.add_node(node_id,
                entity="CPU",
                cpu_id=cpu,
                total_time=metrics['total'],
                idle_time=metrics['idle'],
                busy_time=metrics['busy'],
                utilization=metrics['utilization'])

# Add Thread nodes.
for thread, total_time in thread_metrics.items():
    node_id = f"T_{thread}"
    KG.add_node(node_id,
                entity="Thread",
                thread_id=thread,
                total_cpu_time=total_time)

# Add edges from Thread to CPU.
for (thread, cpu), metrics in edge_metrics.items():
    source = f"T_{thread}"
    target = f"CPU_{cpu}"
    avg_time = metrics['total_time'] / metrics['count']
    KG.add_edge(source, target,
                relation="used_cpu",
                total_accumulated_time=metrics['total_time'],
                count=metrics['count'],
                avg_accumulated_time=avg_time,
                accumulated_times=metrics['accumulated_times'])

# =============================================================================
# STEP 4: PRINT METRICS AND VISUALIZE THE KNOWLEDGE GRAPH
# =============================================================================

print("\n=== CPU Metrics ===")
for cpu, metrics in cpu_metrics.items():
    print(
        f"CPU {cpu}: Total = {metrics['total']} ns, Idle = {metrics['idle']} ns, Busy = {metrics['busy']} ns, Utilization = {metrics['utilization']:.2f}%")

print("\n=== Thread Metrics ===")
for thread, total_time in thread_metrics.items():
    print(f"Thread {thread}: Latest accumulated CPU time = {total_time} ns")

print("\n=== Edge Metrics (Thread -> CPU) ===")
for (thread, cpu), metrics in edge_metrics.items():
    avg_time = metrics['total_time'] / metrics['count']
    print(
        f"Thread {thread} -> CPU {cpu}: Total accumulated time = {metrics['total_time']} ns, Count = {metrics['count']}, Average = {avg_time:.2f} ns, Recorded values = {metrics['accumulated_times']}")

# Visualize the Knowledge Graph.
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(KG, k=0.5)
# Color nodes: CPUs in red, Threads in green.
node_colors = []
for node in KG.nodes(data=True):
    if node[1]['entity'] == "CPU":
        node_colors.append('red')
    elif node[1]['entity'] == "Thread":
        node_colors.append('green')
    else:
        node_colors.append('grey')
nx.draw(KG, pos, with_labels=True, node_color=node_colors, node_size=1500, arrowsize=20)
plt.title("Knowledge Graph from CPU Usage Analysis")
plt.show()

# =============================================================================
# FINAL NOTES:
# =============================================================================
# - This code replaces "duration" with "accumulated_cpu_time", since the values
#   returned by your state system query are cumulative CPU times up to the query time.
# - If the same thread appears multiple times for the same CPU, we accumulate the
#   total and keep a list of all recorded values, so you can later compute differences if desired.
# - The CPU node metrics include the total recorded time (which ideally should be close
#   to the query interval), idle time (when thread == "0"), busy time, and a computed
#   utilization percentage.
# - You can further modify this code to compute incremental CPU time (by taking differences
#   between successive accumulated values) if that is more meaningful for your analysis.
#
# Run this script in PyCharm on Linux. It uses standard matplotlib (plt.show()) to display the plot.
