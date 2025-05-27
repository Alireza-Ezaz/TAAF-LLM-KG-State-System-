# -------------------- RQ2 DATASET AND PREPARATION --------------------
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data for RQ2
data_rq2 = {
    'Condition': ['Without Schema', 'With Schema'],
    '0s_no_graph': [124, 111],
    '0.5s_no_graph': [66, 29],
    '1s_no_graph': [110, 160],
    '0s_graph': [60, 56],
    '0.5s_graph': [50, 9],
    '1s_graph': [190, 235],
}

df_rq2 = pd.DataFrame(data_rq2)

# Calculate percentages for visualization
for s in ['0', '0.5', '1']:
    df_rq2[f'P{s}_no_graph'] = df_rq2[f'{s}s_no_graph'] / 300 * 100
    df_rq2[f'P{s}_graph'] = df_rq2[f'{s}s_graph'] / 300 * 100

# Accuracy calculation
df_rq2['Acc_no_graph'] = (df_rq2['0.5s_no_graph'] * 0.5 + df_rq2['1s_no_graph']) / 300 * 100
df_rq2['Acc_graph'] = (df_rq2['0.5s_graph'] * 0.5 + df_rq2['1s_graph']) / 300 * 100
df_rq2['Accuracy Improvement (%)'] = df_rq2['Acc_graph'] - df_rq2['Acc_no_graph']

# Color mapping
color_map = {'0': '#d73027', '0.5': '#fee08b', '1': '#1a9850'}

# Create pie charts as an alternative visualization for RQ2
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
score_labels = ['Score 0', 'Score 0.5', 'Score 1']
colors = ['#d73027', '#fee08b', '#1a9850']

# Prepare data for "Without Schema"
sizes_no_schema = [
    df_rq2.loc[0, 'P0_graph'],
    df_rq2.loc[0, 'P0.5_graph'],
    df_rq2.loc[0, 'P1_graph']
]
axes[0].pie(
    sizes_no_schema,
    labels=[f"{label} ({size:.2f}%)" for label, size in zip(score_labels, sizes_no_schema)],
    autopct=None,
    startangle=90,
    colors=colors,
    wedgeprops={'edgecolor': 'black'}
)
axes[0].set_title("TAAF with KG - Without Graph Schema",fontweight='bold')

# Prepare data for "With Schema"
sizes_with_schema = [
    df_rq2.loc[1, 'P0_graph'],
    df_rq2.loc[1, 'P0.5_graph'],
    df_rq2.loc[1, 'P1_graph']
]
axes[1].pie(
    sizes_with_schema,
    labels=[f"{label} ({size:.2f}%)" for label, size in zip(score_labels, sizes_with_schema)],
    autopct=None,
    startangle=90,
    colors=colors,
    wedgeprops={'edgecolor': 'black'}
)
axes[1].set_title("TAAF with KG - With Graph Schema", fontweight='bold')

# Add annotation of improvement
improvement = df_rq2.loc[1, 'Accuracy Improvement (%)']
fig.suptitle(f"Effect of Graph Schema on Accuracy (Improvement: +{improvement:.2f}%)", fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()
