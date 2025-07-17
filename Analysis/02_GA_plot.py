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
num = 100      # 実行回数 / Number of GA runs
bias = 4       # ファイル名のオフセット / Offset for file names

# --- データ読み込み / Load result data ---
# created by 01_main_ELAGAopt.py
best_list = []
for i in range(num):
    # 目的関数値の読み込み / Load objective function values
    best_pd = pd.read_csv(f"ELAGAopt_result\\GA_result\\objective_function\\test_data\\best_1000_all_ROI13_{i+bias}.0.csv", index_col=0, header=0)
    best_pd.columns = ["Objective value (|β variance| + Accuracy)"]
    best_list.append(best_pd)

# --- 全実行分を連結 / Concatenate all runs ---
best_all = pd.concat(best_list, axis=1)
best_all.columns = [f"Run{i+bias}" for i in range(num)]

# --- 目的関数値の推移をプロット / Plot objective value history ---
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

