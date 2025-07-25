"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for comparing ROI selection results between ASD and CTL groups
----------------------------------------------------
From the ELA optimization results, this script evaluates the Ising model fit accuracy and parameter variance for each group,
----------------------------------------------------
"""
import pandas as pd
import numpy as np
import random
import elagaopt as elaopt
from multiprocessing import Pool


def main():
    random.seed(1000)

    # --- Path settings ---
    pkl_path = "Data//test_data_3//binary_data"
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_3"
    output_dir = "ELAGAopt_result//Analysis_result//ASD_CTL_compare"
    task_data_1 = []
    task_data_2 = []

    # --- Load brain activity data ---
    task_data_1, task_data_2,_ = elaopt.load_brain_data(pkl_path, group_split=True)
    print(f"\nTotal files loaded: group1={len(task_data_1)}, group2={len(task_data_2)}")

    var_list_g1, acc_list_g1, num_list_g1, val_list_g1 = [], [], [], []
    var_list_g2, acc_list_g2, num_list_g2, val_list_g2 = [], [], [], []

    # --- Evaluate for each individual ---
    for k in range(100):
        individual_df = pd.read_csv(f"{ga_result_path}//best_ind_1000_all_ROI12_1_{k+4}.0.csv")
        individual = individual_df.iloc[999].values
        individual = np.delete(individual, 0)

        result_g1, acc_g1, num_g1 = elaopt.func_ELA(individual=individual, task_data_train=task_data_1)
        result_g2, acc_g2, num_g2 = elaopt.func_ELA(individual=individual, task_data_train=task_data_2)

        print(f"result g1: var={result_g1}, acc={acc_g1}, sum={result_g1 + acc_g1}, num={num_g1}")
        print(f"result g2: var={result_g2}, acc={acc_g2}, sum={result_g2 + acc_g2}, num={num_g2}")

        var_list_g1.append(result_g1)
        acc_list_g1.append(acc_g1)
        num_list_g1.append(num_g1)
        val_list_g1.append(result_g1 + acc_g1)

        var_list_g2.append(result_g2)
        acc_list_g2.append(acc_g2)
        num_list_g2.append(num_g2)
        val_list_g2.append(result_g2 + acc_g2)

    # --- Convert to DataFrame and save ---
    var_df = pd.DataFrame({'ASD': var_list_g1, 'CTL': var_list_g2})
    acc_df = pd.DataFrame({'ASD': acc_list_g1, 'CTL': acc_list_g2})
    num_df = pd.DataFrame({'ASD': num_list_g1, 'CTL': num_list_g2})
    val_df = pd.DataFrame({'ASD': val_list_g1, 'CTL': val_list_g2})

    print(var_df)

    var_df.to_csv(f"{output_dir}//var_ASD_CTL.csv", index=False)
    acc_df.to_csv(f"{output_dir}//acc_ASD_CTL.csv", index=False)
    num_df.to_csv(f"{output_dir}//num_ASD_CTL.csv", index=False)
    val_df.to_csv(f"{output_dir}//val_ASD_CTL.csv", index=False)

if __name__ == "__main__":
    main()