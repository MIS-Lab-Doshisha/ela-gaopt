"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for calculating local minima frequency for each ROI set
----------------------------------------------------
For each individual (ROI set) selected by GA, this script calculates the frequency
of local minima from all subjects' brain activity data and saves the results as a pkl file.
----------------------------------------------------
"""

import pandas as pd
import numpy as np
import pickle
import os
import random
import elagaopt as elaopt

def func_ELA(individual, task_data_train):
    """
    Calculate frequency of local minima for each individual (ROI set)
    """
    # --- Create mask for selected ROIs ---
    selection_mask = np.array(individual, dtype=bool)
    # --- Extract only selected ROIs for each subject ---
    filter_list = [data[selection_mask].astype('int32') for data in task_data_train]
    # --- Concatenate all subjects' data column-wise ---
    task_data = np.concatenate(filter_list, axis=1)
    task_data = pd.DataFrame(task_data)
    task_data.columns = range(task_data.shape[1])
    print(f"task data shape: {task_data.shape}")
    # --- Fit Ising model parameters ---
    h, W = elaopt.fit_approx_new(task_data)
    graph, num = elaopt.calc_basin_graph(h, W, task_data)
    print(graph)
    # --- Calculate local minima frequency for each subject ---
    freq_df = pd.DataFrame()
    for i, filtered in enumerate(filter_list):
        filter_df = pd.DataFrame(filtered)
        localmin_list = []
        for column_name, item in filter_df.items():
            n = len(item)
            decimal_value = sum(v * (2**(n - 1 - i)) for i, v in enumerate(item))
            result = graph[graph['source'] == decimal_value]['state_no']
            localmin_list.append(int(result.values))
        # --- Count occurrences ---
        counts = {}
        for num in localmin_list:
            counts[num] = counts.get(num, 0) + 1
        # --- Calculate frequency ---
        total_count = len(localmin_list)
        frequencies = {num: count / total_count for num, count in counts.items()}
        freq_result = pd.DataFrame({
            f'Frequency_{i+1}': list(frequencies.values())
        }, index=list(counts.keys()))
        freq_result.index.name = 'Number'
        freq_df = pd.concat([freq_df, freq_result], axis=1)
    return freq_df

def main():

    random.seed(1000)
    # --- Path settings ---
    pkl_path = "Data//test_data_2//binary_data"
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_2"
    output_path = "ELAGAopt_result//Analysis_result//local_min_freq_data//freq_ROI13.pkl"

    # --- Load brain activity data ---
    task_data_all,_ = elaopt.load_brain_data(pkl_path, group_split=False)

    freq_list = []
    n_individuals = 100  # Number of individuals
    for k in range(n_individuals):
        # --- Load GA-selected individual ---
        individual_path = os.path.join(ga_result_path, f"best_ind_1000_all_ROI13_{k+4}.0.csv")
        individual_df = pd.read_csv(individual_path)
        individual = individual_df.iloc[999].values
        individual = np.delete(individual, 0)
        # --- Calculate local minima frequency ---
        freq_df = func_ELA(individual=individual, task_data_train=task_data_all)
        freq_list.append(freq_df)
        print(f"Processed individual {k+1}/{n_individuals}")

    # --- Save results as pkl file ---
    with open(output_path, "wb") as f:
        pickle.dump(freq_list, f)
    print("All frequency data saved.")

if __name__ == "__main__":
    main()