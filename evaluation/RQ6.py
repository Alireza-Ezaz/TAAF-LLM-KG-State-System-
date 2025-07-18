import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Data for TAAF (with graph) at different temporal locations
data = {
    'Location': ['Start (5s)', 'Mid (middle)', 'End (15s before end)'],
    'Count_0': [60, 54, 45],
    'Count_0.5': [18, 16, 21],
    'Count_1': [222, 230, 234]
}
df = pd.DataFrame(data)
df['Accuracy (%)'] = (df['Count_0.5'] * 0.5 + df['Count_1']) / 300 * 100

# Line chart with y-axis starting at 60%
fig, ax = plt.subplots(figsize=(8, 4))
x = np.arange(len(df))
locations = df['Location'].tolist()
accuracy = df['Accuracy (%)'].to_numpy()

ax.plot(x, accuracy, marker='o', linestyle='-', linewidth=2)
ax.fill_between(x, accuracy, alpha=0.2)

# Set y-axis from 60 to 100
ax.set_ylim(60, 100)

# Annotate points slightly above
for i, value in enumerate(accuracy):
    ax.text(i, value + 1.5, f"{value:.1f}%", ha='center', fontsize=10)

ax.set_xticks(x)
ax.set_xticklabels(locations, rotation=15)
ax.set_ylabel('Accuracy (%)')
ax.set_title('TAAF Accuracy at Different Temporal Locations\n(60–100% scale)')
ax.grid(True, axis='y')

plt.tight_layout()
plt.savefig("../evaluation_outputs/RQ6.pdf", format="pdf")  # Save as vector PDF
plt.show()