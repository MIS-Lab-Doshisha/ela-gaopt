""" 
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for evaluating and visualizing ROI-selected individuals
----------------------------------------------------
Calculates Ising model fit accuracy, variance of individual parameters, 
and number of local minima from brain activity data and GA-selected ROI individuals.
-----------------------------------------------------
"""

import pandas as pd
import numpy as np
import os
import random
import elagaopt as elaopt

# --- Function to evaluate individuals ---
def evaluate_individuals(individual_dir, n_individuals, task_data_all, output_dir, prefix=""):
    """
    Evaluate each individual using Ising model and save results
    """
    var_list = []
    acc_list = []
    num_list = []
    val_list = []
    for k in range(n_individuals):
        individual_path = os.path.join(individual_dir, f"best_ind_var_1000_{k+2}.0.csv")
        individual_df = pd.read_csv(individual_path)
        individual = individual_df.iloc[999].values
        individual = np.delete(individual, 0)
        result, acc, num = elaopt.func_ELA(individual=individual, task_data_train=task_data_all)
        print(f"result {prefix} : var={result}, acc={acc}, var+acc={result + acc}, num={num}")
        var_list.append(result)
        acc_list.append(acc)
        num_list.append(num)
        val_list.append(result + acc)
    # --- Convert results to DataFrame and save ---
    var_df = pd.DataFrame(var_list)
    acc_df = pd.DataFrame(acc_list)
    num_df = pd.DataFrame(num_list)
    val_df = pd.DataFrame(val_list)
    print(var_df)
    # --- Save to CSV if needed ---
    var_df.to_csv(os.path.join(output_dir, f"var_opt_{prefix}.csv"), index=False)
    acc_df.to_csv(os.path.join(output_dir, f"acc_opt_{prefix}.csv"), index=False)
    num_df.to_csv(os.path.join(output_dir, f"num_opt_{prefix}.csv"), index=False)
    val_df.to_csv(os.path.join(output_dir, f"val_opt_{prefix}.csv"), index=False)

def main():
    random.seed(1000)
    
    # --- Path settings ---
    pkl_path = "Data//test_data_1//discovery"
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_1"
    output_path = "ELAGAopt_result//Analysis_result//objective_function"
    n_individuals = 100  # Change as needed
    task_data_all, _ = elaopt.load_brain_data(pkl_path, group_split=False)
    evaluate_individuals(ga_result_path, n_individuals, task_data_all, output_path, prefix="train_s1")

if __name__ == "__main__":
    main()