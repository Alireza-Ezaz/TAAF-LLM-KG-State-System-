# -------------------- RQ3 DATASET AND PREPARATION --------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Construct data
data_rq3 = {
    'Model': ['GPT 4.1 nano', 'GPT 4o', 'GPT o4-mini'] * 3,
    'Time Interval': ['1s'] * 3 + ['10s'] * 3 + ['100s'] * 3,
    '0s_no_graph': [125, 111, 55, 166, 119, 92, 148, 137, 108],
    '0.5s_no_graph': [54, 29, 47, 43, 41, 26, 48, 40, 30],
    '1s_no_graph': [121, 160, 198, 91, 140, 182, 104, 123, 162],
    '0s_graph': [102, 56, 8, 140, 54, 16, 136, 61, 23],
    '0.5s_graph': [33, 9, 11, 17, 16, 16, 20, 17, 13],
    '1s_graph': [165, 235, 281, 143, 230, 268, 144, 222, 264]
}

# Create DataFrame
df_rq3 = pd.DataFrame(data_rq3)

# Compute accuracies
df_rq3['Acc_no_graph'] = (df_rq3['0.5s_no_graph'] * 0.5 + df_rq3['1s_no_graph']) / 300 * 100
df_rq3['Acc_graph'] = (df_rq3['0.5s_graph'] * 0.5 + df_rq3['1s_graph']) / 300 * 100
df_rq3['Accuracy_Improvement (%)'] = df_rq3['Acc_graph'] - df_rq3['Acc_no_graph']

# Prepare data for heatmap
model_order = ['GPT 4.1 nano', 'GPT 4o', 'GPT o4-mini']
interval_order = ['1s', '10s', '100s']

heatmap_data = df_rq3.pivot(index="Model", columns="Time Interval", values="Acc_graph")
heatmap_data = heatmap_data.loc[model_order[::-1], interval_order]  # Reverse model order for correct vertical layout

# -------------------- RQ3 HEATMAP PLOT --------------------
plt.figure(figsize=(8, 5))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap=sns.light_palette("blue", as_cmap=True),
    cbar_kws={'label': 'Accuracy with Graph (%)'}
)
plt.title("TAAF Accuracy Across Models and Time Intervals (With Knowledge Graph)", fontsize=13)
plt.xlabel("Time Interval")
plt.ylabel("Model")
plt.tight_layout()
plt.show()
