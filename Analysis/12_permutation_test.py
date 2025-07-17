"""
Permutationテストによる目的関数値の有意性検定・可視化スクリプト 
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
ランダム個体とELA/GAopt個体の目的関数値（例: Isingモデル適合度＋パラメータ分散）の分布を比較し、
t検定・マンホイットニーU検定・Permutationテスト・Cohen's d計算・可視化を行います。

Script for significance testing and visualization of objective function values using permutation test
---------------------------------------------------------------------------------------------------
Compares the distribution of objective function values (e.g., Ising model fit + parameter variance) between random and ELA/GAopt individuals,
performs t-test, Mann-Whitney U test, permutation test, calculates Cohen's d, and visualizes the results.
"""

import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats


def main(seed):
    random.seed(seed)
    np.random.seed(seed)
    # --- データ読み込み / Load data ---
    # created by 10_permutation_random_data_create.py, 11_random_roi_selection.py
    # random_dataはランダムに選択されたROI個体の目的関数
    random_data_acc = np.array(pd.read_csv("ELAGAopt_result//Analysis_result//random_ROI_selection//acc_random_train_s1.csv",header=0))
    random_data_beta = np.array(pd.read_csv("ELAGAopt_result//Analysis_result//random_ROI_selection//var_random_train_s1.csv",header=0))
    random_data =  random_data_beta + random_data_acc

    # --- ELA/GAopt個体の目的関数値読み込み / Load ELA/GAopt objective function values ---
    # created by 06_ELAGAopt_result_check.py
    # exp_dataはELA/GAoptで選択されたROI個体の目的関数
    exp_data_acc = np.array(pd.read_csv("ELAGAopt_result//Analysis_result//objective_function//acc_opt_train_s1.csv",header=0))
    exp_data_beta = np.array(pd.read_csv("ELAGAopt_result//Analysis_result//objective_function//var_opt_train_s1.csv",header=0))
    exp_data = exp_data_beta + exp_data_acc

    print(f"Random data length : {len(random_data)}, mean :{np.mean(random_data)}, std :{np.std(random_data)}")
    print(f"Experience data length : {len(exp_data)},mean :{np.mean(exp_data)}, std :{np.std(exp_data)}")

    # --- 統計検定 / Statistical tests ---
    t_stat, p_ttest = stats.ttest_ind(exp_data.flatten(), random_data.flatten(), equal_var=False)
    print(f"Welchのt検定: t値 = {t_stat:.4f}, p値 = {p_ttest}")
    u_stat, p_mwu = stats.mannwhitneyu(exp_data.flatten(), random_data.flatten(), alternative='two-sided')
    print(f"マン・ホイットニーU検定: U値 = {u_stat:.4f}, p値 = {p_mwu}")

    # --- Permutationテスト / Permutation test ---
    T_obs = np.mean(exp_data) - np.mean(random_data)
    print(np.mean(random_data), np.mean(exp_data), T_obs)

    all_scores = np.concatenate([random_data, exp_data])  
    n_permutations = 10000
    perm_diffs = np.zeros(n_permutations)

    for i in range(n_permutations):
        np.random.shuffle(all_scores)
        perm_diffs[i] = np.mean(all_scores[:len(exp_data)]) - np.mean(all_scores[len(exp_data):])
    print(np.abs(perm_diffs) >= np.abs(T_obs))

    p_value = np.mean((perm_diffs) >= (T_obs))
    print(f"観測された差: {T_obs:.4f}")
    print(f"p値: {p_value}")

    # --- ヒストグラムの可視化 / Histogram visualization ---
    plt.hist(perm_diffs, bins=50, color='#b8b8b8', alpha=0.7)
    plt.axvline(T_obs, color='black', linestyle='--')
    plt.title(f'Permutation Test\np = {p_value}')
    plt.xlabel('Difference in Means (ELA/GAopt - Random)')
    plt.ylabel('Frequency')
    plt.tick_params(axis='both', direction='in')
    plt.tight_layout()
    plt.show()

    # --- ボックスプロット・蜂群図の可視化 / Boxplot & swarmplot visualization ---
    acc_list = [exp_data_acc.flatten(),random_data_acc.flatten()]
    beta_list = [exp_data_beta.flatten(),random_data_beta.flatten()]
    eva_list = [exp_data.flatten(),random_data.flatten()] 

    fig, ax = plt.subplots(figsize=(5, 8))
    plot_data = pd.DataFrame({
        'Value': np.concatenate([random_data.flatten(), exp_data.flatten()]),
        'Group': (["Random ROI"] * len(random_data.flatten())) + \
                (["ELA/GAopt-selected ROI"] * len(exp_data.flatten()))
    })
    order = ["Random ROI", "ELA/GAopt-selected ROI"]

    sns.boxplot(
        x='Group',
        y='Value',
        data=plot_data,
        ax=ax,
        palette=['#8cc5e3', '#1a80bb'],
        boxprops=dict(edgecolor='none'),
        medianprops=dict(color='white', linewidth=2),
        showfliers=False,
        order=order
    )
    sns.swarmplot(
        x='Group',
        y='Value',
        data=plot_data,
        ax=ax,
        palette=['#0072B2', '#003366'],
        size=5,
        alpha=0.8,
        order=order
    )

    ax.set_xticklabels(order)
    ax.set_ylabel("Objective function values")
    ax.set_title("Objective function values (Test data)")
    ax.tick_params(axis='both', direction='in')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # --- 有意差を示す線と＊を追加 / Add significance bar ---
    y_max = max(np.max(exp_data), np.max(random_data))
    y_min = min(np.min(exp_data), np.min(random_data))
    h = (y_max - y_min) * 0.05
    y = y_max + h

    x1, x2 = 0, 1
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='k', zorder=20)

    plt.tight_layout()
    plt.show()

    # --- 効果量（Cohen's d）計算 / Calculate effect size (Cohen's d) ---
    mean1 = np.mean(exp_data)
    mean2 = np.mean(random_data)
    std1 = np.std(exp_data, ddof=1)
    std2 = np.std(random_data, ddof=1)
    n1 = len(exp_data)
    n2 = len(random_data)
    pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))
    cohens_d = (mean1 - mean2) / pooled_std
    print(f"Cohen's d: {cohens_d:.4f}")

if __name__ == "__main__":
    # シード値を指定してmainを実行 / Run main with specified seed
    seed = 100
    main(seed)