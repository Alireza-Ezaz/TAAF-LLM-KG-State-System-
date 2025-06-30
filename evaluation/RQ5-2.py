import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1) Load data
csv_path = "../extra_documents/TAAF Aggregated Results.csv"
df = pd.read_csv(csv_path)

# 2) Accuracy helper
def add_accuracy(frame, zero_col, half_col, one_col, new_name):
    frame[new_name] = (
        0.5 * frame[half_col] + 1 * frame[one_col]
    ) / (frame[[zero_col, half_col, one_col]].sum(axis=1)) * 100
    return frame

add_accuracy(df, 'Raw 0s',          'Raw 0.5',          'Raw 1s',          'Acc_NoKG')
add_accuracy(df, 'KG-Powered 0s',   'KG-Powered 0.5s',  'KG-Powered 1s',   'Acc_KG')

# 3) Aggregate by query-type & graph-structure
agg = (
    df.groupby(['Question Category Type', 'Question Graph Type'])
      [['Acc_NoKG', 'Acc_KG']]
      .mean()
      .reset_index()
)

# Nice order
query_order = ['Explanation', 'Multiple Choice', 'True/False']
graph_order = ['Single-Hub', 'Multi-Hub']
agg['Question Category Type'] = pd.Categorical(agg['Question Category Type'], query_order, ordered=True)
agg['Question Graph Type']    = pd.Categorical(agg['Question Graph Type'],    graph_order, ordered=True)
agg.sort_values(['Question Category Type', 'Question Graph Type'], inplace=True)

# -------------- CHART A – Clustered grouped bars --------------
plt.figure(figsize=(10, 6))
bar_w = 0.2
x = range(len(query_order))
palette = sns.color_palette("husl", 8)

for i, g in enumerate(graph_order):
    sub = agg[agg['Question Graph Type'] == g]
    # No-KG (hatched)
    plt.bar([p + i*bar_w        for p in x], sub['Acc_NoKG'], width=bar_w,
            label=f'{g} (No KG)', color=palette[i*2], hatch='//', edgecolor='black')
    # With KG (solid)
    plt.bar([p + i*bar_w + bar_w for p in x], sub['Acc_KG'],  width=bar_w,
            label=f'{g} (With KG)', color=palette[i*2], edgecolor='black')

plt.xticks([p + bar_w for p in x], query_order)
plt.ylabel("Accuracy (%)")
plt.title("Accuracy by Query Type & Graph Structure\n(Solid = With KG, Hatched = No KG)")
plt.ylim(0, 100)
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
plt.tight_layout()
plt.show()

# -------------- CHART B – Diverging bar of KG gain --------------
agg['Delta'] = agg['Acc_KG'] - agg['Acc_NoKG']
plt.figure(figsize=(8, 6))
sns.barplot(data=agg, y='Question Category Type', x='Delta',
            hue='Question Graph Type', palette="Blues_r", orient='h')
plt.axvline(0, color='black', linewidth=0.7)
plt.xlabel("Accuracy Gain from Knowledge Graph (pp)")
plt.ylabel("Query Type")
plt.title("Knowledge-Graph Accuracy Gain per Query Type & Graph Structure")
plt.legend(title="Graph Structure")
plt.tight_layout()
plt.savefig("../Result Pictures/RQ5-2.pdf", format="pdf")  # Save as vector PDF
plt.show()
