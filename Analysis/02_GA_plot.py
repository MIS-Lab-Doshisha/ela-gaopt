"""
--------------------------------------------------
Tested with Python 3.13.2
--------------------------------------------------
Script for visualizing only the objective function value in GA optimization history
--------------------------------------------------
Visualizes generation-wise history of objective function value (|β variance| + Accuracy) for multiple GA runs.
--------------------------------------------------
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --- Variable settings ---
num = 100      # Number of GA runs
bias = 4       # Offset for file names

# --- Load result data ---
# created by 01_main_ELAGAopt.py
best_list = []
for i in range(num):
    # Load objective function values
    best_pd = pd.read_csv(f"ELAGAopt_result\\GA_result\\objective_function\\test_data\\best_1000_all_ROI13_{i+bias}.0.csv", index_col=0, header=0)
    best_pd.columns = ["Objective value (|β variance| + Accuracy)"]
    best_list.append(best_pd)

# --- Concatenate all runs ---
best_all = pd.concat(best_list, axis=1)
best_all.columns = [f"Run{i+bias}" for i in range(num)]

# --- Plot objective value history ---
plt.figure(figsize=(10, 6))
colors = sns.color_palette("viridis", num)
for i in range(num):
    plt.plot(best_all.index, best_all.iloc[:, i], label=f"Run {i+bias}", color=colors[i], alpha=0.8)
plt.xlabel("Generation")
plt.ylabel("Objective value (|β variance| + Accuracy)")
plt.title("GA Convergence of Objective Function")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

