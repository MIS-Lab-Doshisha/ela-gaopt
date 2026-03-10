""" 
----------------------------------------------------
Tested with Python 3.13.2
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
import elagaopt as elaopt
from statannotations.Annotator import Annotator
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # --- Path settings ---
    # Atlas ROI label file
    # Using existing atlas label file
    #atlas_label_path = "Data//atlas_data//power264NodeNames.txt"

    # --- GA optimization result file pattern ---
    # created by 01_main_ELAGAopt.py
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_4//best_ind_1000_all_ROI12_2_{idx}.0.csv"
    scenario_num =40  # Scenario number used in GA optimization
    # --- Load random ROI selection data for comparison ---
    random_roi_path = "ELAGAopt_result//Analysis_result//random_ROI_selection//roi_random_s3.csv"
    random_roi_df = pd.read_csv(random_roi_path)
    n_individuals = 100  # Number of individuals/trials
    individual_all_df = pd.DataFrame()
    seed = 42
    random.seed(seed)
    for i in range(n_individuals):
        print(f"Processing individual {i+1}/{n_individuals}")
        individual_path = ga_result_path.format(idx=i+4)
        individual_df = pd.read_csv(individual_path)
        individual = individual_df.iloc[999].values
        individual = np.delete(individual, 0)  # Remove index column if present
        print(f"Individual data shape: {individual.shape}")
        print(f"Number of selected ROIs: {np.sum(individual)}")
        print(F"individual data preview: {individual[:10]} ...")
        print(f"Selected ROIs for individual {i+1}: {np.where(individual == 1)[0]}")

        # Store individual data in a DataFrame
        individual_df = pd.DataFrame([individual])
        individual_all_df = pd.concat([individual_all_df, individual_df], ignore_index=True)
    # --- Calculate stability metrics ---
    output_path_prefix = f"ELAGAopt_result//Analysis_result//selected_ROI_stability//stability_metrics_s{scenario_num}"
    hamming_select, jaccard_select = caluculate_stability_metrics(individual_all_df, output_path_prefix, scenario_num=scenario_num)

    random_path_prefix = f"ELAGAopt_result//Analysis_result//selected_ROI_stability//stability_metrics_random_s{scenario_num}"
    hamming_random, jaccard_random = caluculate_stability_metrics(random_roi_df, random_path_prefix, scenario_num=scenario_num)
    # --- Boxplot comparison ---
    boxplot_comparison(hamming_select, hamming_random,"Hamming Distance", scenario_num=scenario_num)
    boxplot_comparison(jaccard_select, jaccard_random,"Jaccard Index", scenario_num=scenario_num)
    boxplot_comparison_summary(hamming_select, hamming_random,jaccard_select, jaccard_random, scenario_num=scenario_num)

def caluculate_stability_metrics(individual_all_df, output_path_prefix,scenario_num=1):
    """
    Calculate and save stability metrics (Hamming distance and Jaccard index) for selected ROIs across individuals.
    """
    n_individuals = individual_all_df.shape[0]
    hamming_distances = np.zeros((n_individuals, n_individuals))
    jaccard_indices = np.zeros((n_individuals, n_individuals))

    for i in range(n_individuals):
        for j in range(n_individuals):
            if i != j:
                # Hamming distance
                hamming_distances[i, j] = np.sum(individual_all_df.iloc[i] != individual_all_df.iloc[j])
                # Jaccard index
                intersection = np.sum((individual_all_df.iloc[i] == 1) & (individual_all_df.iloc[j] == 1))
                union = np.sum((individual_all_df.iloc[i] == 1) | (individual_all_df.iloc[j] == 1))
                jaccard_indices[i, j] = intersection / union if union != 0 else 0
                #print(f"Computed metrics for individuals {i+1} and {j+1}")
                #print(f"Hamming distance: {hamming_distances[i, j]}, Jaccard index: {jaccard_indices[i, j]}")
                #print(f"intersection: {intersection}, union: {union}")
                #print(f"Selected ROIs for individual {i}: {np.where(individual_all_df.iloc[i] == 1)[0]}")
                #print(f"Selected ROIs for individual {j}: {np.where(individual_all_df.iloc[j] == 1)[0]}")

    # Save results
    hamming_df = pd.DataFrame(hamming_distances)
    jaccard_df = pd.DataFrame(jaccard_indices)

    hamming_df.to_csv(f"{output_path_prefix}_hamming_distances.csv", index=False)
    jaccard_df.to_csv(f"{output_path_prefix}_jaccard_indices.csv", index=False)
    print("Stability metrics saved.")
    print(f"mean Hamming distance: {hamming_df.values.mean()}")
    print(f"mean Jaccard index: {jaccard_df.values.mean()}")
    return hamming_df, jaccard_df

def boxplot_comparison_summary(select_ham_df, random_ham_df,select_jac_df,random_jac_df, scenario_num=1):
    # Create summary data for both Hamming and Jaccard metrics
    select_upper_ham = select_ham_df.where(np.triu(np.ones(select_ham_df.shape), k=1).astype(bool)).stack().reset_index(drop=True)
    random_upper_ham = random_ham_df.where(np.triu(np.ones(random_ham_df.shape), k=1).astype(bool)).stack().reset_index(drop=True)
    select_upper_jac = select_jac_df.where(np.triu(np.ones(select_jac_df.shape), k=1).astype(bool)).stack().reset_index(drop=True)
    random_upper_jac = random_jac_df.where(np.triu(np.ones(random_jac_df.shape), k=1).astype(bool)).stack().reset_index(drop=True)
    print(f"Selected ROIs Hamming upper triangle data length: {len(select_upper_ham)}")
    print(f"Random ROIs Hamming upper triangle data length: {len(random_upper_ham)}")
    print(f"Selected ROIs Jaccard upper triangle data length: {len(select_upper_jac)}")
    print(f"Random ROIs Jaccard upper triangle data length: {len(random_upper_jac)}")

    # ボックスプロットの作成
    order = ["Random", "ELA/GAopt"]
    data_ham = pd.DataFrame({"Metric": "Hamming Distance",
            "Group": np.repeat(order, [len(random_upper_ham), len(select_upper_ham)]),
            "Value": pd.concat([random_upper_ham, select_upper_ham], ignore_index=True)
           })
    data_jac = pd.DataFrame({"Metric": "Jaccard Index",
            "Group": np.repeat(order, [len(random_upper_jac), len(select_upper_jac)]),
            "Value": pd.concat([random_upper_jac, select_upper_jac], ignore_index=True)
           })
    fig,ax = plt.subplots(1,2, figsize=(12, 6))
    # Hamming Distance plot
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
    size=1,       # 点を小さく
    order=order
    )"""
    """sns.stripplot(
    x='Group',
    y='Value',
    data=data_ham,
    ax=ax[0],
    palette=['#0072B2', '#003366'],
    alpha=0.5,
    jitter=0.45,   # 左右の広がりを制御
    order=order
    )"""
    ax[0].tick_params(direction='in',length=6)
    ax[0].tick_params(axis='x', width=0.5,length=3)
    ax[0].set_ylabel("Hamming Distance", fontsize=15)
    ax[0].set_xlabel("")
    # ax[0].set_title("Hamming Distance", fontsize=18)
    # Jaccard Index plot
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
    size=1,       # 点を小さく
    order=order
    )"""   
    """sns.stripplot(
    x='Group',
    y='Value',
    data=data_jac,
    ax=ax[1],
    palette=['#0072B2', '#003366'],
    alpha=0.5,
    jitter=0.45,   # 左右の広がりを制御
    order=order
    )"""
    ax[1].tick_params(direction='in',length=6)
    ax[1].tick_params(axis='x', width=0.5,length=3)
    ax[1].set_ylabel("Jaccard Index", fontsize=15)
    ax[1].set_xlabel("")
    # ax[1].set_title("Jaccard Index", fontsize=18)
    annotator = Annotator(
        ax[0],
        [("Random", "ELA/GAopt")], 
        data=data_ham,
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
    ax[0], test_results_ham = annotator.annotate()
    print("Hamming Distance comparison results:")
    for res in test_results_ham:
        print(res.data)
    annotator_jac = Annotator(
        ax[1],
        [("Random", "ELA/GAopt")],
        data=data_jac,
        x="Group",
        y="Value",
        verbose=False
    )
    annotator_jac.configure(
        test="Mann-Whitney",
        text_format="star",
        loc="inside",
        comparisons_correction="fdr_bh",
        pvalue_thresholds=[[1e-4, "****"], [1e-3, "***"], [1e-2, "**"], [0.05, "*"], [1, "ns"]]
    )
    annotator_jac.apply_test()
    ax[1], test_results_jac = annotator_jac.annotate()
    print("Jaccard Index comparison results:")
    for res in test_results_jac:
        print(res.data)
    
    for a in ax:
        # x軸のラベル（Random, ELA/GAopt）を取得してループ
        labels = a.get_xticklabels()
        for label in labels:
            label.set_fontsize(18)  # 全体のフォントサイズを大きくする
            if label.get_text() == "ELA/GAopt":
                label.set_weight('bold')  # ELA/GAoptだけ太字にする
        
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
    #plt.savefig(f"ELAGAopt_result//Analysis_result//selected_ROI_stability//boxplot_{prefix.replace(' ','_')}_s{scenario_num}.png", dpi=300)
    #plt.show()
    
if __name__ == "__main__":
    main()