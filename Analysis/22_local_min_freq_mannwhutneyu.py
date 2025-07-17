"""
局所安定状態頻度の群間比較スクリプト
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
各個体の局所安定状態（local minima）頻度データについて、グループ1とグループ2で
Mann-Whitney U検定・効果量r算出・FDR補正を行い、結果をCSVで保存します。

Script for group comparison of local minima frequency
----------------------------------------------------
Performs Mann-Whitney U test, effect size r calculation, and FDR correction
between group 1 and group 2 for local minima frequency data of each individual,
and saves the results as CSV files.
"""

import pandas as pd
import pickle
import os
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

def load_group_labels(pkl_path):
    """グループラベルを読み込む / Load group labels from participant files"""
    id_df = pd.Series(dtype=int)
    for filename in os.listdir(pkl_path):
        if filename.endswith(".pkl"):
            participants_filename = filename.replace("pkl", "tsv")
            participants_filename = "participants_" + participants_filename
            participants_path = os.path.join(pkl_path, participants_filename)
            behavioral_df = pd.read_csv(participants_path, sep="\t", encoding="latin1")
            id_df = pd.concat([id_df, behavioral_df["dx_group"]], ignore_index=True)
    return id_df

def group_comparison(data, group1_indices, group2_indices, output_dir):
    """群間比較とFDR補正を実施し、結果を保存 / Perform group comparison and save results"""
    os.makedirs(output_dir, exist_ok=True)
    result_list = []
    for i in range(len(data)):
        group1_df = data[i].T.iloc[group1_indices].fillna(0)
        group2_df = data[i].T.iloc[group2_indices].fillna(0)

        results_df = pd.DataFrame(columns=['Column', 'Statistic', 'P-value', 'r'])

        for column in group1_df.columns:
            if column in group2_df.columns:
                t_statistic, p_value = mannwhitneyu(group1_df[column], group2_df[column])
                n1 = group1_df[column].shape[0]
                n2 = group2_df[column].shape[0]
                N = n1 + n2
                mean_U = n1 * n2 / 2
                std_U = ((n1 * n2 * (N + 1)) / 12) ** 0.5
                z = (t_statistic - mean_U) / std_U
                r = z / N**0.5
                results_df = pd.concat([
                    results_df,
                    pd.DataFrame([{
                        'Column': column,
                        'Statistic': t_statistic,
                        'P-value': p_value,
                        'r': r
                    }])
                ], ignore_index=True)

        # FDR補正 / FDR correction
        if not results_df.empty:
            reject, pvals_corrected, _, _ = multipletests(results_df['P-value'], alpha=0.05, method='fdr_bh')
            results_df['FDR_P-value'] = pvals_corrected

        # 個体ごとにCSV保存 / Save each individual's result as CSV
        results_df.to_csv(os.path.join(output_dir, f"local_min_group_comparison_{i+1}.csv"), index=False)
        result_list.append(results_df)
    return result_list

def main():
    # --- パス設定 / Path settings ---
    pkl_path = "Data//scenario_2//binary_data"
    # created by 21_local_min_freq_calc.py
    # 局所安定状態頻度データのパス / Path to local minima frequency data
    freq_data_path = "ELAGAopt_result//Analysis_result//local_min_freq_data//freq_ROI13.pkl"
    output_path = "ELAGAopt_result//Analysis_result//local_min_group_comparison_results"

    # グループラベルの読み込み / Load group labels
    id_df = load_group_labels(pkl_path)
    group1_indices = id_df[id_df == 1].index.tolist()
    group2_indices = id_df[id_df == 2].index.tolist()

    # 局所安定状態頻度データの読み込み / Load local minima frequency data
    with open(freq_data_path, "rb") as f:
        data = pickle.load(f)

    # 群間比較と結果保存 / Perform group comparison and save results
    result_list = group_comparison(data, group1_indices, group2_indices, output_path)

    # 例：特定個体の結果を表示 / Example: print result for individual 79 and 98
    print(result_list[78])
    print(result_list[97])

if __name__ == "__main__":
    main()