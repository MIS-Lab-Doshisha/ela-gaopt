""" 
選択されたROIの安定性分析スクリプト
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
----------------------------------------------------
Script for analyzing stability of selected ROIs across trials
----------------------------------------------------
calculates frequency of ROI selections using hamming distance and jaccard index
-----------------------------------------------------
"""

import pandas as pd
import numpy as np
import os
import random
#import elagaopt as elaopt
from statannotations.Annotator import Annotator
import matplotlib.pyplot as plt
import seaborn as sns

# --- main関数 / Main function ---
def main():
    # --- パス設定/Path settings ---
    # Atlas ROI label file
    # Using existing atlas label file
    atlas_label_path = "Data//atlas_data//power264NodeNames.txt"

    # --- GA最適化結果ファイルパターン / GA optimization result file pattern ---
    # created by 01_main_ELAGAopt.py
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//best_ind_{idx}.csv"
    scenario_num = 1  # Scenario number used in GA optimization

    # --- ランダムROI選択結果の読み込み / Load random ROI selection results ---
    random_roi_path = "ELAGAopt_result//Analysis_result//random_ROI_selection//roi_random_s1_600.csv"
    random_roi_df = pd.read_csv(random_roi_path)
    n_individuals = 100  # Number of individuals/trials
    individual_all_df = pd.DataFrame()

    # --- GA最適化されたROI選択結果の読み込み / Load GA-optimized ROI selection results ---
    for i in range(n_individuals):
        print(f"Processing individual {i+1}/{n_individuals}")
        individual_path = ga_result_path.format(idx=i+1)                                # パスを生成 / Generate path for the individual
        individual_df = pd.read_csv(individual_path)                                    # 個体データを読み込む / Load individual data   
        individual = individual_df.iloc[999].values                                     # 最終世代の個体を抽出 / Extract the individual from the final generation
        individual = np.delete(individual, 0)                                           # 最初の列（インデックス）を削除 / Remove the first column (index)
        print(f"Individual data shape: {individual.shape}") 
        print(f"Number of selected ROIs: {np.sum(individual)}")
        print(F"individual data preview: {individual[:10]} ...")
        print(f"Selected ROIs for individual {i+1}: {np.where(individual == 1)[0]}")

        individual_df = pd.DataFrame([individual])                                              # 個体データをDataFrame化 / Convert individual data to DataFrame
        individual_all_df = pd.concat([individual_all_df, individual_df], ignore_index=True)    # GA最適化された個体データを結合 / Concatenate GA-optimized individual data

    # --- 安定性指標の計算と保存 / Calculate and save stability metrics ---
    output_path_prefix = f"ELAGAopt_result//Analysis_result//selected_ROI_stability//stability_metrics_s{scenario_num}"
    hamming_select, jaccard_select = caluculate_stability_metrics(individual_all_df, output_path_prefix, scenario_num=scenario_num)
    random_path_prefix = f"ELAGAopt_result//Analysis_result//selected_ROI_stability//stability_metrics_random_s{scenario_num}"
    hamming_random, jaccard_random = caluculate_stability_metrics(random_roi_df, random_path_prefix, scenario_num=scenario_num)

    # --- 安定性指標のボックスプロット作成 / Create boxplots for stability metrics ---
    boxplot_comparison(hamming_select, hamming_random,"Hamming Distance", scenario_num=scenario_num)
    boxplot_comparison(jaccard_select, jaccard_random,"Jaccard Index", scenario_num=scenario_num)
    boxplot_comparison_summary(hamming_select, hamming_random,jaccard_select, jaccard_random, scenario_num=scenario_num)

# --- 安定性指標の計算関数 / Function to calculate stability metrics ---
def caluculate_stability_metrics(individual_all_df, output_path_prefix,scenario_num=1):
    """
    Calculate and save stability metrics (Hamming distance and Jaccard index) for selected ROIs across individuals.
    """
    n_individuals = individual_all_df.shape[0]                      # 個体数を取得 / Get number of individuals
    hamming_distances = np.zeros((n_individuals, n_individuals))    # Hamming距離の行列を初期化 / Initialize matrix for Hamming distances
    jaccard_indices = np.zeros((n_individuals, n_individuals))      # Jaccard指数の行列を初期化 / Initialize matrix for Jaccard indices

    # --- 個体間のHamming距離とJaccard指数を計算 / Calculate Hamming distance and Jaccard index between individuals ---
    for i in range(n_individuals):
        for j in range(n_individuals):
            if i != j:
                hamming_distances[i, j] = np.sum(individual_all_df.iloc[i] != individual_all_df.iloc[j])        # Hamming距離の計算 / Calculate Hamming distance
                intersection = np.sum((individual_all_df.iloc[i] == 1) & (individual_all_df.iloc[j] == 1))      # Jaccard指数の分子（共通の選択されたROIの数） / Numerator for Jaccard index (number of commonly selected ROIs)
                union = np.sum((individual_all_df.iloc[i] == 1) | (individual_all_df.iloc[j] == 1))             # Jaccard指数の分母（少なくとも一方で選択されたROIの数） / Denominator for Jaccard index (number of ROIs selected in at least one individual)
                jaccard_indices[i, j] = intersection / union if union != 0 else 0                               # Jaccard指数の計算 / Calculate Jaccard index (handle division by zero) 
                #print(f"Computed metrics for individuals {i+1} and {j+1}")
                #print(f"Hamming distance: {hamming_distances[i, j]}, Jaccard index: {jaccard_indices[i, j]}")
                #print(f"intersection: {intersection}, union: {union}")
                #print(f"Selected ROIs for individual {i}: {np.where(individual_all_df.iloc[i] == 1)[0]}")
                #print(f"Selected ROIs for individual {j}: {np.where(individual_all_df.iloc[j] == 1)[0]}")

    # --- 結果をDataFrame化して保存 / Convert results to DataFrame and save ---
    hamming_df = pd.DataFrame(hamming_distances)
    jaccard_df = pd.DataFrame(jaccard_indices)
    hamming_df.to_csv(f"{output_path_prefix}_hamming_distances.csv", index=False)
    jaccard_df.to_csv(f"{output_path_prefix}_jaccard_indices.csv", index=False)
    print("Stability metrics saved.")
    print(f"mean Hamming distance: {hamming_df.values.mean()}")
    print(f"mean Jaccard index: {jaccard_df.values.mean()}")
    return hamming_df, jaccard_df

# --- ボックスプロット作成関数 / Function to create boxplots for stability metrics ---
def boxplot_comparison_summary(select_ham_df, random_ham_df,select_jac_df,random_jac_df, scenario_num=1):
    # --- 上三角行列を取得 / Extract upper triangle of the matrices ---
    select_upper_ham = select_ham_df.where(np.triu(np.ones(select_ham_df.shape), k=1).astype(bool)).stack().reset_index(drop=True) # 上三角行列を抽出して1次元化 / Extract upper triangle and flatten to 1D
    random_upper_ham = random_ham_df.where(np.triu(np.ones(random_ham_df.shape), k=1).astype(bool)).stack().reset_index(drop=True) # 上三角行列を抽出して1次元化 / Extract upper triangle and flatten to 1D
    select_upper_jac = select_jac_df.where(np.triu(np.ones(select_jac_df.shape), k=1).astype(bool)).stack().reset_index(drop=True) # 上三角行列を抽出して1次元化 / Extract upper triangle and flatten to 1D
    random_upper_jac = random_jac_df.where(np.triu(np.ones(random_jac_df.shape), k=1).astype(bool)).stack().reset_index(drop=True) # 上三角行列を抽出して1次元化 / Extract upper triangle and flatten to 1D
    print(f"Selected ROIs Hamming upper triangle data length: {len(select_upper_ham)}")
    print(f"Random ROIs Hamming upper triangle data length: {len(random_upper_ham)}")
    print(f"Selected ROIs Jaccard upper triangle data length: {len(select_upper_jac)}")
    print(f"Random ROIs Jaccard upper triangle data length: {len(random_upper_jac)}")

    # --- ボックスプロットの作成 / Create boxplots ---
    order = ["Random", "ELA/GAopt"]                                                     # グループの順序を指定 / Specify order of groups                    
    data_ham = pd.DataFrame({"Metric": "Hamming Distance",                              
            "Group": np.repeat(order, [len(random_upper_ham), len(select_upper_ham)]),
            "Value": pd.concat([random_upper_ham, select_upper_ham], ignore_index=True)
           })
    data_jac = pd.DataFrame({"Metric": "Jaccard Index",
            "Group": np.repeat(order, [len(random_upper_jac), len(select_upper_jac)]),
            "Value": pd.concat([random_upper_jac, select_upper_jac], ignore_index=True)
           })
    fig,ax = plt.subplots(1,2, figsize=(12, 6)) # ボックスプロットの作成 / Create boxplots
    
    # --- Hamming距離のプロット / Hamming distance plot ---
    sns.violinplot(
        x='Group',
        y='Value',
        data=data_ham,
        ax=ax[0],
        palette=['#8cc5e3', '#1a80bb'],
        inner=None, # バイオリン内部のデフォルト描画を消す
        linewidth=1.5,
        order=order
    )
    sns.boxplot(
        x='Group',
        y='Value',
        data=data_ham,
        ax=ax[0],
        width=0.15, # 箱の幅を狭くする
        color='white',
        boxprops=dict(edgecolor="#000000", facecolor='white', linewidth=1.5, zorder=2),
        medianprops=dict(color='#000000', linewidth=2, zorder=2),       # 中央値の横線
        whiskerprops=dict(color='#000000', linewidth=1.5, zorder=2),    # ヒゲの縦線
        capprops=dict(color='#000000', linewidth=1.5, zorder=2),        # 最大最小の横線
        flierprops=dict(marker='o', markerfacecolor='#000000', markeredgecolor='none', markersize=5, zorder=2), # 外れ値のドット
        showcaps=True,   # ヒゲの先端の横線を表示
        showfliers=False, 
        order=order
    )
    """sns.swarmplot(
        x='Group',
        y='Value',
        data=data_ham,
        ax=ax[0],
        palette=['#0072B2', '#003366'],
        alpha=0.8,
        order=order
    )"""

    ax[0].tick_params(direction='in',length=6)          # ティックを内側に向ける / Set ticks to point inward
    ax[0].tick_params(axis='x', width=0.5,length=3)     # x軸のティックを細く短くする / Make x-axis ticks thinner and shorter
    ax[0].set_ylabel("Hamming Distance", fontsize=15)   # y軸ラベルを設定 / Set y-axis label
    ax[0].set_xlabel("")                                # x軸ラベルを空にする / Set x-axis label to empty       
    # ax[0].set_title("Hamming Distance", fontsize=18)
    # Jaccard Index plot

    # --- Jaccard指数のプロット / Jaccard index plot ---
    sns.violinplot(
        x='Group',
        y='Value',
        data=data_jac,
        ax=ax[1],
        palette=['#8cc5e3', '#1a80bb'],
        inner=None,
        linewidth=1.5,
        order=order
    )
    sns.boxplot(
        x='Group',
        y='Value',
        data=data_jac,
        ax=ax[1],
        width=0.15,
        color='white',
        boxprops=dict(edgecolor='#000000', facecolor='white', linewidth=1.5, zorder=2),
        medianprops=dict(color='#000000', linewidth=2, zorder=2),       # 中央値の横線
        whiskerprops=dict(color='#000000', linewidth=1.5, zorder=2),    # ヒゲの縦線
        capprops=dict(color='#000000', linewidth=1.5, zorder=2),        # 最大最小の横線
        flierprops=dict(marker='o', markerfacecolor='#000000', markeredgecolor='none', markersize=5, zorder=2), # 外れ値のドット
        showcaps=True,   # ヒゲの先端の横線を表示
        showfliers=False, 
        order=order
    )
    """sns.swarmplot(
        x='Group',
        y='Value',
        data=data_jac,
        ax=ax[1],
        palette=['#0072B2', '#003366'],
        alpha=0.8,
        order=order
    )"""

    ax[1].tick_params(direction='in',length=6)          # ティックを内側に向ける / Set ticks to point inward
    ax[1].tick_params(axis='x', width=0.5,length=3)     # x軸のティックを細く短くする / Make x-axis ticks thinner and shorter
    ax[1].set_ylabel("Jaccard Index", fontsize=15)      # y軸ラベルを設定 / Set y-axis label
    ax[1].set_xlabel("")                                # x軸ラベルを空にする / Set x-axis label to empty
    # ax[1].set_title("Jaccard Index", fontsize=18) 

    # --- 有意差を示す線と＊を追加 / Add significance bars ---
    annotator = Annotator(
        ax[0],
        [("Random", "ELA/GAopt")], 
        data=data_ham,
        x="Group",
        y="Value",
        verbose=False
    )
    # --- Mann-Whitney U検定を適用して有意差を表示 / Apply Mann-Whitney U test and display significance ---
    annotator.configure(
        test="Mann-Whitney",
        text_format="star",
        loc="inside",
        comparisons_correction="fdr_bh",
        pvalue_thresholds=[[1e-4, "****"], [1e-3, "***"], [1e-2, "**"], [0.05, "*"], [1, "ns"]]
    )

    annotator.apply_test()                              # テストを適用 / Apply the test
    ax[0], test_results_ham = annotator.annotate()      # 結果をプロットに反映 / Annotate the plot with results
    print("Hamming Distance comparison results:")
    
    # --- p値の計算と表示 / Print the results of the comparison ---
    for res in test_results_ham:                    
        print(res.data)
    
    # --- Jaccard指数の有意差表示 / Significance display for Jaccard index ---
    annotator_jac = Annotator(
        ax[1],
        [("Random", "ELA/GAopt")],
        data=data_jac,
        x="Group",
        y="Value",
        verbose=False
    )
    # --- Mann-Whitney U検定を適用して有意差を表示 / Apply Mann-Whitney U test and display significance ---
    annotator_jac.configure(
        test="Mann-Whitney",
        text_format="star",
        loc="inside",
        comparisons_correction="fdr_bh",
        pvalue_thresholds=[[1e-4, "****"], [1e-3, "***"], [1e-2, "**"], [0.05, "*"], [1, "ns"]]
    )

    annotator_jac.apply_test()                            # テストを適用 / Apply the test    
    ax[1], test_results_jac = annotator_jac.annotate()    # 結果をプロットに反映 / Annotate the plot with results
    print("Jaccard Index comparison results:")
    
    # --- p値の計算と表示 / Print the results of the comparison ---
    for res in test_results_jac:
        print(res.data)
    
    # --- x軸のラベルを大きくして、ELA/GAoptだけ太字にする / Enlarge x-axis labels and make ELA/GAopt bold ---
    for a in ax:
        labels = a.get_xticklabels()            # x軸のティックラベルを取得 / Get x-axis tick labels
        for label in labels:
            label.set_fontsize(18)              # 全てのラベルのフォントサイズを大きくする / Enlarge font size for all labels
            if label.get_text() == "ELA/GAopt": # ELA/GAoptのラベルを太字にする / Make ELA/GAopt label bold
                label.set_weight('bold')        # 太字に設定 / Set to bold
        
        # y軸のティックラベルも大きくしたい場合は以下を追加
        a.tick_params(axis='y', labelsize=16)
    plt.tight_layout()
    plt.savefig(f"ELAGAopt_result//Analysis_result//selected_ROI_stability//boxplot_stability_metrics_summary_s{scenario_num}.png", dpi=300)
    plt.savefig(f"ELAGAopt_result//Analysis_result//selected_ROI_stability//boxplot_stability_metrics_summary_s{scenario_num}.svg", dpi=300)
    
    plt.show()

def boxplot_comparison(select_df, random_df,prefix, scenario_num=1):
    # 上三角行列を取得
    select_upper = select_df.where(np.triu(np.ones(select_df.shape), k=1).astype(bool)).stack().reset_index(drop=True)
    random_upper = random_df.where(np.triu(np.ones(random_df.shape), k=1).astype(bool)).stack().reset_index(drop=True)
    print(f"Selected ROIs upper triangle data length: {len(select_upper)}")
    print(f"Selected ROIs upper triangle data preview: {select_upper[:10]} ...")
    print(f"Random ROIs upper triangle data length: {len(random_upper)}")
    print(f"Random ROIs upper triangle data preview: {random_upper[:10]} ...")

    # ボックスプロットの作成
    order = ["Random ROI", "ELA/GAopt-selected ROI"]

    data = pd.DataFrame({"Group": np.repeat(order, [len(random_upper), len(select_upper)]),
            "Value": pd.concat([random_upper, select_upper], ignore_index=True)
           })
    print(f"Boxplot data preview:\n{pd.DataFrame(data)}")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(
        x='Group',
        y='Value',
        data=data,
        ax=ax,
        palette=['#8cc5e3', '#1a80bb'],
        boxprops=dict(edgecolor='none'),
        medianprops=dict(color='white', linewidth=2),
        showfliers=False,
        order=order
    )
    """sns.swarmplot(
        x='Group',
        y='Value',
        data=data,
        ax=ax,
        palette=['#0072B2', '#003366'],
        alpha=0.8,
        order=order
    )"""
    annotator = Annotator(
        ax, 
        [("Random ROI", "ELA/GAopt-selected ROI")], 
        data=data,
        x="Group", 
        y="Value",
        verbose=False
    )
    annotator.configure(
        test="Mann-Whitney",
        text_format="star",
        loc="inside",
        comparisons_correction="fdr_bh",
        pvalue_thresholds=[[1e-4, "****"], [1e-3, "***"], [1e-2, "**"], [0.05, "*"], [1, "ns"]]
    )

    annotator.apply_test()
    ax, test_results = annotator.annotate()
    print(prefix + " comparison results:")
    # p値の計算と表示
    for res in test_results:
        print(res.data)
    # 効果量の計算（Cohen's d）
    mean_select = select_upper.mean()
    mean_random = random_upper.mean()
    std_select = select_upper.std()
    std_random = random_upper.std()
    pooled_std = np.sqrt(((len(select_upper) - 1) * std_select ** 2 + (len(random_upper) - 1) * std_random ** 2) / (len(select_upper) + len(random_upper) - 2))
    cohens_d = (mean_select - mean_random) / pooled_std if pooled_std > 0 else 0
    print(f"Cohen's d for {prefix} comparison: {cohens_d}")
    plt.ylabel(f"{prefix}", fontsize=15)
    plt.tight_layout()
    plt.savefig(f"ELAGAopt_result//Analysis_result//selected_ROI_stability//boxplot_{prefix.replace(' ','_')}_s{scenario_num}.png", dpi=300)
    plt.show()
    
if __name__ == "__main__":
    main()