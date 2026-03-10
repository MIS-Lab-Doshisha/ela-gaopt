"""
GA最適化履歴の目的関数値, Accuracy, β分散の可視化スクリプト 
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
複数回のGA実行結果の目的関数値（|β分散| + Accuracy）, Accuracy, β分散の世代ごとの推移を可視化します。

Script for visualizing objective function value, accuracy, and β variance in GA optimization history
----------------------------------------------------------------------------------
Visualizes generation-wise history of objective function value (|β variance| + Accuracy) for multiple GA runs.
"""

import matplotlib.pyplot as plt
from matplotlib import gridspec
import pandas as pd
import seaborn as sns

# --- パラメータ設定 / Parameters ---
num = 1        # 実行回数 / Number of GA runs
bias = 0       # ファイル名のオフセット / Offset for file names

# --- データ読み込み / Load result data ---
# created by 01_main_ELAGAopt.py
best_list = []
acc_list = []
var_list = []
trial_list = ["1"]  # 行回数に応じて変更 / Modify according to number of runs
for i in trial_list:
    i = int(i)
    # 目的関数値の読み込み / Load objective function values
    best_pd = pd.read_csv(f"ELAGAopt_result//GA_result//objective_function//best_fitness_{i}.csv", header=0)
    best_pd.columns = ["Objective value (|β variance| + Accuracy)"]
    best_list.append(best_pd)
    acc_pd = pd.read_csv(f"ELAGAopt_result//GA_result//acc//acc_train_1000_{i}.csv", header=0,index_col=0)
    acc_pd.columns = ["Accuracy"]
    acc_list.append(acc_pd)
    var_pd = pd.read_csv(f"ELAGAopt_result//GA_result//var//var_train_1000_{i}.csv", header=0,index_col=0)
    var_pd.columns = ["|β variance|"]
    var_list.append(var_pd)


# --- 全実行分を連結 / Concatenate all runs ---
best_all = pd.concat(best_list, axis=1)
best_all.columns = [f"Run{i}" for i in trial_list]
acc_all = pd.concat(acc_list, axis=1)
acc_all.columns = [f"Run{i}" for i in trial_list]
var_all = pd.concat(var_list, axis=1)
var_all.columns = [f"Run{i}" for i in trial_list]

# --- 目的関数値の推移をプロット / Plot objective value history ---
plt.figure(figsize=(10, 6))
colors = sns.color_palette("viridis", n_colors=len(trial_list))
for i in range(len(trial_list)):
    plt.plot(best_all.index, best_all.iloc[:, i], label=f"Run {i}", color=colors[i], alpha=0.8)
plt.xlabel("Generation")
plt.ylabel("Objective value (|β variance| + Accuracy)")
plt.title("GA Convergence of Objective Function")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()
plt.savefig("ELAGAopt_result/Analysis_result/GA_plot/convergence_plot.png", dpi=300)

# --- best, beta, accの3つのグラフを1つの画像にまとめる（上：best、下：varとaccを横並び） / Combine best, beta, and acc graphs into one image (top: best, bottom: var and acc side by side) ---
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(2, 2, height_ratios=[2, 1], width_ratios=[1, 1])

colors = sns.color_palette("viridis", num)

# --- 上段（best）：2列分使う / Top row (best): use 2 columns ---
ax_best = fig.add_subplot(gs[0, :])
for i in range(num):
    ax_best.plot(best_all.index, best_all.iloc[:, i], label=f"Run {i+bias}", color=colors[i], alpha=0.8)
ax_best.set_xlabel("Generation")
ax_best.set_ylabel("Objective function (|β variance| + Accuracy)")
ax_best.set_title("GA Convergence of Objective Function (Scenario 1)")
ax_best.grid(True, linestyle="--", alpha=0.6)

# -- 下段左（β variance） / Bottom left (β variance)---
ax_var = fig.add_subplot(gs[1, 0])
for i in range(num):
    ax_var.plot(var_all.index, var_all.iloc[:, i], color=colors[i], alpha=0.8)
ax_var.set_xlabel("Generation")
ax_var.set_ylabel("β Variance")
ax_var.set_title("GA Convergence of β Variance")
ax_var.grid(True, linestyle="--", alpha=0.6)

# --- 下段右（Accuracy） / Bottom right (Accuracy)---
ax_acc = fig.add_subplot(gs[1, 1])
for i in range(num):
    ax_acc.plot(acc_all.index, acc_all.iloc[:, i], color=colors[i], alpha=0.8)
ax_acc.set_xlabel("Generation")
ax_acc.set_ylabel("Accuracy")
ax_acc.set_title("GA Convergence of Accuracy")
ax_acc.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("ELAGAopt_result/Analysis_result/GA_plot/convergence_all_plot.png", dpi=300)
plt.savefig("ELAGAopt_result/Analysis_result/GA_plot/convergence_all_plot.png", dpi=300)


