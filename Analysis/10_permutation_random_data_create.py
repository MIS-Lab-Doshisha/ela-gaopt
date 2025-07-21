"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for generating permutation test data using random ROI-selected individuals
----------------------------------------------------
Calculates Ising model fit accuracy and parameter variance for randomly selected ROIs, and saves the results as CSV files.
----------------------------------------------------
"""

import pandas as pd
import numpy as np
import elagaopt as elaopt
import random


def main(seed):
    random.seed(seed)
    min_values = []
    # --- Path settings ---
    pkl_path = "Data//test_data_1//discovery"
    # Use load_brain_data function here
    task_data_all, _ = elaopt.load_brain_data(pkl_path, group_split=False)
    print(f"\nTotal files loaded: {len(task_data_all)}")
    acc_list = []
    var_list = []
    value_list = []
    num_list = []
    # --- Evaluate 100 random individuals ---
    for i in range(100):
        # --- Generate random individual (10 ones, rest zeros) ---
        ones = [1] * 10
        zeros = [0] * (160 - 10)
        individual = ones + zeros
        random.shuffle(individual)
        print(len(individual))
        # --- Create mask for selected ROIs ---
        selection_mask = np.array(individual, dtype=bool)
        # --- Extract only selected ROIs for each subject ---
        filter_list = [data[selection_mask].astype('int32') for data in task_data_all]
        # --- Concatenate all subjects' data column-wise ---
        task_data = np.concatenate(filter_list, axis=1)
        task_data = pd.DataFrame(task_data)
        print(f"Iteration {i+1}: Train shape = {task_data.shape}")
        task_data.columns = range(task_data.shape[1])
        print(task_data.shape)
        # --- Fit Ising model ---
        h, W = elaopt.fit_approx_new(task_data)
        acc1, acc2 = elaopt.calc_accuracy(h, W, task_data)
        print(f"data : acc1 = {acc1}")
        print(f"data : acc2 = {acc2}")
        print(f"data : acc1+acc2/2 = {(acc1+acc2)/2}")
        # --- Calculate variance and accuracy --
        result, acc,num = elaopt.func_ELA(individual=individual, task_data_train=task_data_all)
        print(f"data : beta variance = {result}")
        print(f"data : acc1+acc2/2 = {acc}")
        
        acc_list.append(acc)
        var_list.append(result)
        value_list.append(acc+result)
        num_list.append(num)

        # --- Save results periodically ---
        if i % 1 == 0:
            acc_df = pd.DataFrame(acc_list)
            var_df = pd.DataFrame(var_list)
            value_df = pd.DataFrame(value_list)
            num_df = pd.DataFrame(num_list)
            acc_df.to_csv("ELAGAopt_result//Analysis_result//random_ROI_selection//acc_random_train_s1.csv", index=False)
            var_df.to_csv("ELAGAopt_result//Analysis_result//random_ROI_selection//var_random_train_s1.csv", index=False)
            value_df.to_csv("ELAGAopt_result//Analysis_result//random_ROI_selection//value_random_train_s1.csv", index=False)
            num_df.to_csv("ELAGAopt_result//Analysis_result//random_ROI_selection//num_random_train_s1.csv", index=False)


if __name__ == "__main__":
    # --- Run main with specified seed ---
    seed = 800
    for i in range(1):
        main(seed)
      