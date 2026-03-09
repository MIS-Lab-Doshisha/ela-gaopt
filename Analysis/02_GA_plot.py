"""
GA最適化履歴の目的関数値可視化スクリプト 
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
複数回のGA実行結果の目的関数値（|β分散| + Accuracy）の世代ごとの推移を可視化します。

Script for visualizing only the objective function value in GA optimization history
----------------------------------------------------------------------------------
Visualizes generation-wise history of objective function value (|β variance| + Accuracy) for multiple GA runs.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --- パラメータ設定 / Parameters ---
bias = 0       # ファイル名のオフセット / Offset for file names

# --- データ読み込み / Load result data ---
# created by 01_main_ELAGAopt.py
best_list = []
trial_list = ["4", "5", "6", "7", "8","9", "10","11","12","13","14","15", "16","17","18","19","20","21","22","23","24","25",
              "26","27","28","29","30","31", "32", "33", "34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50", 
              "51","52","53","54","55","56","57", "58", "59", "60","61","62","63","64","65","66","67","68","69","70", "71", "72","73","74","75",
              "76", "77", "78","79","80","81","82","83", "84", "85", "86","87","88","89","90","91","92","93","94","95","96","97","98","99", "100",
              "101","102","103","104"
              ]  # 行回数に応じて変更 / Modify according to number of runs

for i in trial_list:
    i = int(i)
    # 目的関数値の読み込み / Load objective function values
    best_pd = pd.read_csv(f"ELAGAopt_result//GA_result//objective_function//test_data//best_1000_all_ROI13_{i}.0.csv", header=0,index_col=0)
    best_pd.columns = ["Objective value (|β variance| + Accuracy)"]
    best_list.append(best_pd)

# --- 全実行分を連結 / Concatenate all runs ---
best_all = pd.concat(best_list, axis=1)
best_all.columns = [f"Run{i}" for i in trial_list]

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
plt.savefig("ELAGAopt_result/Analysis_result/GA_plot/convergence_plot.png", dpi=300)
plt.show()

