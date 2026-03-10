"""
選択されたROIの個体、もしくはランダムに選択されたROIの個体を評価するスクリプト
-----------------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
Script to evaluate individuals with selected ROIs or randomly selected ROIs
-----------------------------------------------------------
this script evaluates individuals that have either selected ROIs or randomly selected ROIs.
It loads the binarized task data, extracts features based on the individual's selection, 
fits an Ising model, calculates metrics such as beta variance and accuracy, 
and compares local minima between training and test data using various distance metrics. 
The results are saved as CSV files for further analysis.

"""

import pandas as pd
import numpy as np
import pickle
import GA_class as elaopt
import random
import os   

def main(seed):
    random.seed(seed)

    # --- データ読み込み / Load binarized task data ---
    with open("Data//test_data_4//Run01//test//test_data_run01.pkl", "rb") as file:
        task_data_test_original = pickle.load(file)
    with open("Data//test_data_4//Run01//train//train_data_run01.pkl", "rb") as file:
        task_data_train_original = pickle.load(file)
    ga_result_path = "ELAGAopt_result//GA_result//best_individual"
    ham_list = []
    ham_norm_list = []
    jaccard_list = []
    beta_list = []
    inter_list = [] 
    acc_list = []
    val_list = []
    ROI_list = []

    # --- 100個体の評価ループ / Loop to evaluate 100 individuals ---
    for i in range(100):
        # 100個体のCSVファイルから個体を読み込み / Load individual from CSV file for 100 individuals
        individual_path = os.path.join(ga_result_path, f"best_ind_{i+1}.csv")
        individual_df = pd.read_csv(individual_path, header=0,index_col=None)
        individual = individual_df.iloc[999].values
        # ランダムに15個の特徴を選択する個体を生成 / Generate an individual that randomly selects 15 features
        #ones = [1] * 15
        #zeros = [0] * (264 - 15)
        #individual = ones + zeros
        #random.shuffle(individual)
        ROI_list.append(individual)     # 選択されたROI個体を保存 / Save selected ROI individual
        
        # --- 個体で選択された特徴のみ抽出 / Extract only features selected by the individual ---
        filter_array = np.array(individual, dtype=bool)                                     # 個体をブール配列に変換 / Convert individual to boolean array
        filter_train_list = [data[filter_array] for data in task_data_train_original]       # 個体で選択された特徴を抽出 / Extract features selected by the individual
        filter_test_list = [data[filter_array] for data in task_data_test_original]         # 個体で選択された特徴を抽出 / Extract features selected by the individual

        # --- データを結合しDataFrame化 / Concatenate and convert to DataFrame ---
        task_data_train = np.hstack(filter_train_list).astype('int32')                      # 個体で選択された特徴を結合 / Concatenate features selected by the individual
        task_data_test = np.hstack(filter_test_list).astype('int32')                        # 個体で選択された特徴を結合 / Concatenate features selected by the individual
        task_data_train = pd.DataFrame(task_data_train)                                     # 個体で選択された特徴をDataFrame化 / Convert features selected by the individual to DataFrame
        task_data_test = pd.DataFrame(task_data_test)                                       # 個体で選択された特徴をDataFrame化 / Convert features selected by the individual to DataFrame                          
        task_data_train.columns = range(task_data_train.shape[1])                           # 個体で選択された特徴の列名を0からの連番に変更 / Rename columns of features selected by the individual to sequential numbers starting from 0
        task_data_test.columns = range(task_data_test.shape[1])                             # 個体で選択された特徴の列名を0からの連番に変更 / Rename columns of features selected by the individual to sequential numbers starting from 0    

        # --- Isingモデルのパラメータ推定 / Fit Ising model ---
        h_train, W_train = elaopt.fit_approx_new(task_data_train)                           # 訓練データでIsingモデルのパラメータを推定 / Fit Ising model parameters with training data
        h_test, W_test = elaopt.fit_approx_new(task_data_test)                              # テストデータでIsingモデルのパラメータを推定 / Fit Ising model parameters with test data    

        # --- β分散・精度の計算 / Calculate beta variance and accuracy ---
        result_test, acc_test, _ = elaopt.func_ELA(individual=individual, task_data_train=task_data_test_original)          # テストデータで個体を評価 / Evaluate individual with test data
        result_train, acc_train, _ = elaopt.func_ELA(individual=individual, task_data_train=task_data_train_original)       # 訓練データで個体を評価 / Evaluate individual with training data

        # --- 局所安定状態のグラフ計算 / Calculate local minima graph ---
        graph_train, _ = elaopt.calc_basin_graph(h_train, W_train, task_data_train)         # 訓練データで局所安定状態のグラフを計算 / Calculate local minima graph with training data
        graph_test, _ = elaopt.calc_basin_graph(h_test, W_test, task_data_test)             # テストデータで局所安定状態のグラフを計算 / Calculate local minima graph with test data

        # --- 局所安定状態のインデックス取得 / Get indices of local minima ---
        _, train_10 = elaopt.plot_local_min_s1(task_data_train, graph_train)                # 訓練データで局所安定状態のインデックスを取得 / Get indices of local minima with training data 
        _, test_10 = elaopt.plot_local_min_s1(task_data_test, graph_test)                   # テストデータで局所安定状態のインデックスを取得 / Get indices of local minima with test data
        
        # --- set化して比較用に保存 / Convert to set for comparison ----
        set_train = set(train_10)                                                           # 訓練データの局所安定状態のインデックスをset化 / Convert indices of local minima with training data to set
        set_test = set(test_10)                                                             # テストデータの局所安定状態のインデックスをset化 / Convert indices of local minima with test data to set

        # --- 共通するlocal minimaの数/Number of common local minima (intersection) ---
        intersection = len(set_train.intersection(set_test))                                # 共通するlocal minimaの数を計算 / Calculate number of common local minima

        # 全体のユニークなlocal minimaの数 (和集合)/ Total unique local minima (union)
        union = len(set_train.union(set_test))                                              # 全体のユニークなlocal minimaの数を計算 / Calculate total unique local minima

        # 検出された総数 / Total detected count
        total_count = len(set_train) + len(set_test)                                        # 検出された総数を計算 / Calculate total detected count

        # --- 正規化指標の計算 ---
        # 1. 従来のハミング距離（対称差の要素数）
        raw_hamming = len(set_train.symmetric_difference(set_test))                         # 従来のハミング距離を計算 / Calculate traditional Hamming distance (number of elements in symmetric difference)
        print(f"Raw Hamming Distance: {raw_hamming}")
        # 2. 正規化ハミング距離 (0.0: 完全一致, 1.0: 重なりゼロ)
        # 検出数に差があっても、その密度ベースでの不一致度を測る
        norm_hamming = raw_hamming / union if union > 0 else 0                              # 正規化ハミング距離を計算 / Calculate normalized Hamming distance (measures dissimilarity based on density even if counts differ)
        
        # 3. Jaccard距離 (集合の重なりに基づいた距離)
        jaccard_dist = 1.0 - (intersection / union) if union > 0 else 0                     # Jaccard距離を計算 / Calculate Jaccard distance (distance based on set overlap)

        print(f"Train/Test local minima count: {len(set_train)} / {len(set_test)}")
        print(f"Jaccard Distance: {jaccard_dist:.4f}, Normalized Hamming: {norm_hamming:.4f}")

    
        # --- 1024次元ベクトル化しハミング距離計算 / Calculate Hamming distance (1024-dim vector) ---
        train_1024 = np.zeros(32768)                                                        # N次元のベクトルをゼロで初期化 / Initialize 1024-dim vector with zeros                                      
        test_1024 = np.zeros(32768)                                                         # N次元のベクトルをゼロで初期化 / Initialize 1024-dim vector with zeros
        train_1024[train_10] = 1                                                            # 訓練データの局所安定状態のインデックスに1をセット / Set 1 at indices of local minima with training data                               
        test_1024[test_10] = 1                                                              # テストデータの局所安定状態のインデックスに1をセット / Set 1 at indices of local minima with test data 
        print(f"Train local minima indices: {train_10}")
        print(f"Test local minima indices: {test_10}")
        hamming_distances = np.sum(train_1024 != test_1024)                                 # ハミング距離を計算 / Calculate Hamming distance

        # --- 結果をリストに追加 / Append results to lists ---
        ham_list.append(hamming_distances)
        ham_norm_list.append(norm_hamming)
        jaccard_list.append(jaccard_dist)
        inter_list.append(intersection) 
        acc_list.append(acc_train)
        beta_list.append(result_train)
        val_list.append(acc_train + result_train)
        
        # --- 定期的にCSV保存 / Save results as CSV files ---
        if i % 1 == 0:
            pd.DataFrame(ham_list).to_csv(f"ELAGAopt_result//Analysis_result//objective_function//hamming_random_s1_re_{seed}.csv", index=False)
            pd.DataFrame(ham_norm_list).to_csv(f"ELAGAopt_result//Analysis_result//objective_function//hamming_norm_opt_s1_re_{seed}.csv", index=False)
            pd.DataFrame(jaccard_list).to_csv(f"ELAGAopt_result//Analysis_result//objective_function//jaccard_random_s1_re_{seed}.csv", index=False)
            pd.DataFrame(inter_list).to_csv(f"ELAGAopt_result//Analysis_result//objective_function//intersection_random_s1_re_{seed}.csv", index=False)
            pd.DataFrame(ROI_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//roi_random_s1_{seed}.csv", index=False)
            pd.DataFrame(acc_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//acc_opt_train_s1.csv", index=False)
            pd.DataFrame(beta_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//var_opt_train_s1.csv", index=False)
            pd.DataFrame(val_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//val_opt_train_s1.csv", index=False)


if __name__ == "__main__":
    # シード値を指定してmainを実行 / Run main with specified seed
    seed = 500
    for i in range(1):
        seed += 100
        main(seed)


