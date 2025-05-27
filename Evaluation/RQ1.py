# -------------------- DATASET AND PREPARATION --------------------
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Raw data construction
data = {
    'Experiment': list(range(1, 10)),
    'Model': ['GPT 4.1 nano', 'GPT 4o', 'GPT o4-mini',
              'GPT 4.1 nano', 'GPT 4o', 'GPT o4-mini',
              'GPT 4.1 nano', 'GPT 4o', 'GPT o4-mini'],
    'Time Interval': ['1s', '1s', '1s', '10s', '10s', '10s', '100s', '100s', '100s'],
    '0s_no_graph': [125, 111, 55, 166, 119, 92, 148, 137, 108],
    '0.5s_no_graph': [54, 29, 47, 43, 41, 26, 48, 40, 30],
    '1s_no_graph': [121, 160, 198, 91, 140, 182, 104, 123, 162],
    '0s_graph': [102, 56, 8, 140, 54, 16, 136, 61, 23],
    '0.5s_graph': [33, 9, 11, 17, 16, 16, 20, 17, 13],
    '1s_graph': [165, 235, 281, 143, 230, 268, 144, 222, 264]
}

df = pd.DataFrame(data)

# Add meaningful labels
df['Label'] = df['Time Interval'] + '-' + df['Model'].map({
    'GPT 4.1 nano': '4.1nano',
    'GPT 4o': '4o',
    'GPT o4-mini': 'o4mini'
})

# Compute average scores
df['Avg_no_graph'] = (df['0s_no_graph'] * 0 + df['0.5s_no_graph'] * 0.5 + df['1s_no_graph']) / 300
df['Avg_graph'] = (df['0s_graph'] * 0 + df['0.5s_graph'] * 0.5 + df['1s_graph']) / 300
df['Acc_no_graph'] = df['Avg_no_graph'] * 100
df['Acc_graph'] = df['Avg_graph'] * 100
df['Accuracy_Improvement (%)'] = df['Acc_graph'] - df['Acc_no_graph']

# Percentages per score
df['P0_no_graph'] = df['0s_no_graph'] / 300 * 100
df['P0.5_no_graph'] = df['0.5s_no_graph'] / 300 * 100
df['P1_no_graph'] = df['1s_no_graph'] / 300 * 100
df['P0_graph'] = df['0s_graph'] / 300 * 100
df['P0.5_graph'] = df['0.5s_graph'] / 300 * 100
df['P1_graph'] = df['1s_graph'] / 300 * 100

# Color mappings
color_map_with_graph = {'0': '#d73027', '0.5': '#fee08b', '1': '#1a9850'}
color_map_no_graph = {'0': '#fc8d59', '0.5': '#fff7bc', '1': '#91cf60'}

# Prepare labels
labels = df['Label']
x = np.arange(len(labels))
width = 0.35

# -------------------- PLOT 1: Accuracy Improvement --------------------

fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.Greens(df['Accuracy_Improvement (%)'] / df['Accuracy_Improvement (%)'].max())

bars = ax.bar(x, df['Accuracy_Improvement (%)'], color=colors)
ax.axhline(0, color='gray', linestyle='--')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45)
ax.set_ylabel('Accuracy Gain (%)')
ax.set_title('Improvement in Accuracy with Knowledge Graph')

for i, v in enumerate(df['Accuracy_Improvement (%)']):
    ax.text(x[i], v + 0.5, f"+{v:.2f}%", ha='center', fontsize=9)

ax.grid(True, axis='y')
plt.tight_layout()
plt.show()
# -------------------- PLOT 2: Reversed Stacked Score Breakdown --------------------

fig, ax = plt.subplots(figsize=(14, 8))
width2 = 0.45  # up from 0.35

# No Graph bars (bottom = correct answers, top = wrong answers)
bottom = np.zeros(len(labels))
for score in ['1', '0.5', '0']:  # Reverse stacking: 1 on bottom
    heights = df[f'P{score}_no_graph']
    bars = ax.bar(x - width2/2, heights, width2,
                  bottom=bottom, label=f'No Graph - Score {score}',
                  color=color_map_no_graph[score], edgecolor='black')
    for idx, rect in enumerate(bars):
        h = rect.get_height()
        if h > 3:
            ax.text(rect.get_x() + rect.get_width()/2,
                    rect.get_y() + h/2, f"{h:.2f}%",
                    ha='center', va='center', fontsize=9)
    bottom += heights

# With Graph bars (same reversed stacking)
bottom = np.zeros(len(labels))
for score in ['1', '0.5', '0']:
    heights = df[f'P{score}_graph']
    bars = ax.bar(x + width2/2, heights, width2,
                  bottom=bottom, label=f'With Graph - Score {score}',
                  color=color_map_with_graph[score], edgecolor='black')
    for idx, rect in enumerate(bars):
        h = rect.get_height()
        if h > 3:
            ax.text(rect.get_x() + rect.get_width()/2,
                    rect.get_y() + h/2, f"{h:.2f}%",
                    ha='center', va='center', fontsize=9)
    bottom += heights

ax.set_ylabel('Response Distribution (%)')
ax.set_title('TAAF Score Breakdown With and Without Knowledge Graph (0 at Top → 1 at Bottom)')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45)
ax.legend(title='Score and Condition', loc='upper left', bbox_to_anchor=(1, 1))
ax.grid(True, axis='y')
plt.tight_layout()
plt.show()