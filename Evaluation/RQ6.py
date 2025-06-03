import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Data for TAAF(with graph) at different temporal locations
data = {
    'Location': ['Start (5s)', 'Mid (middle)', 'End (15s before end)'],
    'Count_0': [60, 54, 45],
    'Count_0.5': [18, 16, 21],
    'Count_1': [222, 230, 234]
}

df = pd.DataFrame(data)

# Calculate percentages
df['P0'] = df['Count_0'] / 300 * 100
df['P0.5'] = df['Count_0.5'] / 300 * 100
df['P1'] = df['Count_1'] / 300 * 100

# Calculate overall accuracy percentage
df['Accuracy (%)'] = (df['Count_0.5'] * 0.5 + df['Count_1']) / 300 * 100

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1, 1.5]})

# ----- Plot 1: Line plot of Accuracy vs. Temporal Location -----
ax1.plot(df['Location'], df['Accuracy (%)'], marker='o', linestyle='-', color='blue')
ax1.set_ylabel('Accuracy (%)')
ax1.set_title('TAAF Accuracy at Different Temporal Locations')
ax1.set_ylim(0, 100)
for i, value in enumerate(df['Accuracy (%)']):
    ax1.text(i, value + 1, f"{value:.2f}%", ha='center', fontsize=10)
ax1.grid(True, axis='y')

# ----- Plot 2: Stacked Bar Chart of Score Distribution -----
bar_width = 0.5
x = np.arange(len(df['Location']))
colors = {'0': '#d73027', '0.5': '#fee08b', '1': '#1a9850'}

# Stacking bottom values
bottom = np.zeros(len(df))
for score, color_key in zip(['P0', 'P0.5', 'P1'], ['0', '0.5', '1']):
    ax2.bar(x, df[score], bar_width, bottom=bottom, label=f'Score {color_key}',
            color=colors[color_key], edgecolor='black')
    # Annotate inside bars
    for i, height in enumerate(df[score]):
        if height > 3:  # Only annotate if the segment is large enough
            ax2.text(x[i], bottom[i] + height / 2, f"{height:.2f}%",
                     ha='center', va='center', fontsize=9)
    bottom += df[score]

ax2.set_xticks(x)
ax2.set_xticklabels(df['Location'])
ax2.set_ylabel('Response Distribution (%)')
ax2.set_title('Score Distribution at Different Temporal Locations')
ax2.legend(title='Score', loc='upper left', bbox_to_anchor=(1, 1))
ax2.set_ylim(0, 100)
ax2.grid(True, axis='y')

plt.tight_layout()
plt.show()
