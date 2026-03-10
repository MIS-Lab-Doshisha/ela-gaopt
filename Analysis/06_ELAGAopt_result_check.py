"""
ROI最良個体の評価・可視化スクリプト 
---------------------------------------------------
脳活動データとGAで選択されたROI最良個体から、Isingモデルの適合度・個体パラメータ分散・局所安定状態数を計算し、結果を表示・保存します。
---------------------------------------------------
動作確認済み/Tested with Python 3.13.2
Script for evaluating and visualizing ROI-selected individuals
-----------------------------------------------------------------------------------
Calculates Ising model fit accuracy, variance of individual parameters, and number of local minima from brain activity data and GA-selected ROI individuals.
"""

import pandas as pd
import numpy as np
import os
import random
import elagaopt as elaopt

# --- 個体評価関数 / Individual evaluation function ---
def evaluate_individuals(individual_dir, n_individuals, task_data_all, output_dir, prefix=""):
    """
    個体ごとにIsingモデル評価を実施し、結果を保存
    Evaluate each individual using Ising model and save results
    """
    # --- 結果保存用リスト / Lists for storing results ---
    var_list = []
    acc_list = []
    num_list = []
    val_list = []

    # --- 個体ごとに評価 / Evaluate each individual ---
    for k in range(n_individuals):
        individual_path = os.path.join(individual_dir, f"best_ind_var_1000_{k+2}.0.csv")            # 個体ファイルのパス / Path to individual file
        individual_df = pd.read_csv(individual_path, header=0,index_col=0)                          # 個体データの読み込み / Load individual data
        individual = individual_df.iloc[999].values                                                 # 最終世代の個体を取得 / Get the individual from the last generation
        #individual = np.delete(individual, 0)
        result, acc, num = elaopt.func_ELA(individual=individual, task_data_train=task_data_all)    # Isingモデル評価 / Evaluate using Ising model
        print(f"result {prefix} : var={result}, acc={acc}, var+acc={result + acc}, num={num}")
        var_list.append(result)                                                                     # 個体パラメータ分散 / Variance of individual parameters
        acc_list.append(acc)                                                                        # Isingモデル適合度 / Ising model fit accuracy
        num_list.append(num)                                                                        # 局所安定状態数 / Number of local minima
        val_list.append(result + acc)                                                               # パラメータ分散と適合度の合計 / Sum of variance and accuracy
    # --- 結果をDataFrame化・保存 / Convert results to DataFrame and save ---
    var_df = pd.DataFrame(var_list)
    acc_df = pd.DataFrame(acc_list)
    num_df = pd.DataFrame(num_list)
    val_df = pd.DataFrame(val_list)
    print(var_df)
    # --- 必要に応じてCSV保存 / Save to CSV if needed ---
    var_df.to_csv(os.path.join(output_dir, f"var_opt_{prefix}.csv"), index=False)
    acc_df.to_csv(os.path.join(output_dir, f"acc_opt_{prefix}.csv"), index=False)
    num_df.to_csv(os.path.join(output_dir, f"num_opt_{prefix}.csv"), index=False)
    val_df.to_csv(os.path.join(output_dir, f"val_opt_{prefix}.csv"), index=False)

# --- 全個体評価関数 / Function to evaluate all individuals ---
def all_evaluate_individuals(ga_result_dir, task_data_train, output_path):
    memo_result = {}                                                                        # 結果のメモ化用辞書 / Dictionary for memoization of results
    memo_acc = {}                                                                           # 適合度のメモ化用辞書 / Dictionary for memoization of accuracy                                           
    for k in range(1):                                                                    # 個体ごとに評価 / Evaluate each individual
        var_list = []                                                                       # 個体パラメータ分散のリスト / List for variance of individual parameters
        acc_list = []                                                                       # Isingモデル適合度のリスト / List for Ising model fit accuracy                                        
        individual_df = pd.read_csv(f"{ga_result_dir}//best_ind_var_1000_{k+2}.0.csv",# 個体データの読み込み / Load individual data 
        index_col=0)

        for i in range(individual_df.shape[0]):                                             # 個体の各行を評価 / Evaluate each row of the individual data
            individual = individual_df.iloc[i].values                                       # 個体の行をnumpy配列として取得 / Get the row of the individual as a numpy array
            #individual = np.delete(individual, 0)                                          # 最初の列がインデックスの場合は削除 / Remove the first column if it's an index
            # individual（numpy配列）を辞書のキーにするため、イミュータブルな tuple に変換
            ind_tuple = tuple(individual)                                                   # 個体をタプルに変換 / Convert individual to tuple for use as dictionary key

            # --- すでに計算済みかチェック / Check if already calculated ---
            if ind_tuple in memo_result:                                                    # すでに計算済みの場合はキャッシュから結果を取得 / If already calculated, get result from cache 
                result = memo_result[ind_tuple]                                             # print(f"Row {i}: Cached result used.") # デバッグ用 / Debug print
                acc = memo_acc[ind_tuple]                                                   # すでに計算済みの場合はキャッシュから適合度を取得 / If already calculated, get accuracy from cache
            else:
                # --- 未計算の場合のみ実行 / If not calculated, execute ---
                print(f"Iter {k}, Row {i}: Calculating...")
                result, acc,_ = elaopt.func_ELA(individual=individual, 
                task_data_train=task_data_train, use_gpu=False)                             # Isingモデル評価 / Evaluate using Ising model

                memo_result[ind_tuple] = result                                             # 結果をメモ化 / Memoize result                               
                memo_acc[ind_tuple] = acc                                                   # 適合度をメモ化 / Memoize accuracy                      

            var_list.append(result)                                                         # 個体パラメータ分散をリストに追加 / Append variance of individual parameters to list   
            acc_list.append(acc)                                                            # Isingモデル適合度をリストに追加 / Append Ising model fit accuracy to list 
            print(result, acc, result + acc)
        
        # --- 既存の保存処理 / Existing save process ---
        var_df = pd.DataFrame(var_list)
        acc_df = pd.DataFrame(acc_list)
        var_df.to_csv(f"{output_path}//var//var_train_1000_{k+1}.csv")
        acc_df.to_csv(f"{output_path}//acc//acc_train_1000_{k+1}.csv")
    
def main():
    random.seed(1000)
    
    # --- パス設定 / Path settings ---
    pkl_path = "Data//test_data_1//test"
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_1"
    output_path = "ELAGAopt_result//Analysis_result//objective_function//"
    n_individuals = 100  # 必要に応じて変更 / Change as needed
    task_data_all, _ = elaopt.load_brain_data(pkl_path, group_split=False)
    all_or_first = "no"  # "all" で全個体評価、その他で最後の個体のみ評価 / "all" for evaluating all individuals, "else" for evaluating only the last individual

    # --- 個体評価の実行 / Execute individual evaluation ---
    if all_or_first == "all":
        all_evaluate_individuals(ga_result_path, task_data_all, output_path)
    else:
        evaluate_individuals(ga_result_path, n_individuals, task_data_all, output_path, prefix="test_cr")

if __name__ == "__main__":
    main()