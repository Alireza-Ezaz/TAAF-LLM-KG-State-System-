import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# -------------------- 1. DATASET DEFINITION --------------------
data = {
    'Temperature': [0.1, 0.3, 0.5, 0.7, 0.9],
    'Count_0':     [41,   59,  54,  62,  54],   # Wrong answers
    'Count_0.5':   [23,   16,  16,  13,  24],   # Partially correct
    'Count_1':     [236,  225, 230, 225, 222]   # Fully correct
}
df = pd.DataFrame(data)

# -------------------- 2. PERCENTAGE CALCULATIONS --------------------
df['P0']   = df['Count_0']   / 300 * 100
df['P0.5'] = df['Count_0.5'] / 300 * 100
df['P1']   = df['Count_1']   / 300 * 100

# -------------------- 3. WEIGHTED ACCURACY --------------------
# Formula: Accuracy (%) = (0.5 * N0.5 + 1 * N1) / Total * 100
df['Accuracy (%)'] = (0.5 * df['Count_0.5'] + df['Count_1']) / 300 * 100

# -------------------- 4. CONSISTENCY METRIC --------------------
# 4.1 Compute Shannon entropy of the distribution (P0, P0.5, P1)
# 4.2 Normalize by log2(3) to get Entropy_norm in [0,1]
# 4.3 Consistency (%) = (1 - Entropy_norm) * 100
df['Entropy']        = df[['P0','P0.5','P1']].astype(float).apply(lambda r: entropy(r, base=2), axis=1)
df['Consistency (%)'] = (1 - df['Entropy'] / np.log2(3)) * 100


# -------------------- 5. CHART 1: Accuracy vs. Consistency --------------------
fig, ax1 = plt.subplots(figsize=(8, 4))
ax2 = ax1.twinx()

# Plot weighted accuracy
ax1.plot(df['Temperature'], df['Accuracy (%)'],
         marker='o', linestyle='-', color='C0', label='Accuracy (%)')
# Plot consistency
ax2.plot(df['Temperature'], df['Consistency (%)'],
         marker='s', linestyle='--', color='C1', label='Consistency (%)')

ax1.set_xlabel('Sampling Temperature')
ax1.set_ylabel('Accuracy (%)')
ax2.set_ylabel('Consistency (%)')
ax1.set_title('TAAF Weighted Accuracy and Consistency vs. Temperature')

ax1.set_xticks(df['Temperature'])
ax1.grid(True, axis='y', linestyle='--', alpha=0.7)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

# Annotate accuracy points
for x, y in zip(df['Temperature'], df['Accuracy (%)']):
    ax1.text(x, y + 0.5, f"{y:.2f}%", ha='center', fontsize=9)

plt.tight_layout()
# Save as vector PDF
# plt.savefig("../Result Pictures/RQ7.pdf", format="pdf")
plt.show()


# -------------------- 6. CHART 2: Stacked Area Distribution --------------------
fig, ax = plt.subplots(figsize=(8, 4))

# Light red, yellow, green for scores 0, 0.5, 1
colors = ['#f4cccc', '#fff2cc', '#d9ead3']
temps = df['Temperature'].to_numpy(dtype=float)
p0, p05, p1 = df['P0'].to_numpy(), df['P0.5'].to_numpy(), df['P1'].to_numpy()

ax.stackplot(temps, p0, p05, p1,
             labels=['Score 0', 'Score 0.5', 'Score 1'],
             colors=colors)

ax.set_xlabel('Sampling Temperature')
ax.set_ylabel('Response Distribution (%)')
ax.set_title('TAAF Response Distribution Across Temperatures')
ax.set_xticks(df['Temperature'])
ax.legend(loc='upper right')
ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# Annotate inside each area
for i, T in enumerate(temps):
    b0 = 0
    b1 = p0[i]
    b2 = b1 + p05[i]
    ax.text(T, b0 + p0[i]/2,   f"{p0[i]:.2f}%",   ha='center', va='center', fontsize=8)
    ax.text(T, b1 + p05[i]/2, f"{p05[i]:.2f}%", ha='center', va='center', fontsize=8)
    ax.text(T, b2 + p1[i]/2,   f"{p1[i]:.2f}%",   ha='center', va='center', fontsize=8)

plt.tight_layout()
# plt.savefig("../evaluation_outputs/RQ7-2.pdf", format="pdf")
plt.show()
