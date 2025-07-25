"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for generating permutation test data using random ROI-selected individuals
----------------------------------------------------
This script fits the Ising model to training and test data for randomly selected ROI individuals,
evaluates the similarity of local minima (Hamming distance), beta variance, and model accuracy, and saves the results as CSV files.
----------------------------------------------------
"""

import pandas as pd
import numpy as np
import pickle
import elagaopt as elaopt
import random

def main(seed):
    random.seed(seed)

    # --- Load binarized task data ---
    with open("Data//test_data_1//test//task_data_test.pkl", "rb") as file:
        task_data_test_original = pickle.load(file)
    with open("Data//test_data_1//discovery//task_data_train.pkl", "rb") as file:
        task_data_train_original = pickle.load(file)

    ham_list = []
    beta_list = []
    acc_list = []
    val_list = []

    # --- Evaluate 100 random individuals ---
    for i in range(100):
        # --- Generate random individual (10 ones, rest zeros) ---
        ones = [1] * 10
        zeros = [0] * (160 - 10)
        individual = ones + zeros
        random.shuffle(individual)

        # --- Extract only features selected by the individual ---
        filter_array = np.array(individual, dtype=bool)
        filter_train_list = [data[filter_array] for data in task_data_train_original]
        filter_test_list = [data[filter_array] for data in task_data_test_original]

        # --- Concatenate and convert to DataFrame ---
        task_data_train = np.hstack(filter_train_list).astype('int32')
        task_data_test = np.hstack(filter_test_list).astype('int32')
        task_data_train = pd.DataFrame(task_data_train)
        task_data_test = pd.DataFrame(task_data_test)
        task_data_train.columns = range(task_data_train.shape[1])
        task_data_test.columns = range(task_data_test.shape[1])

        # --- Fit Ising model ---
        h_train, W_train = elaopt.fit_approx_new(task_data_train)
        h_test, W_test = elaopt.fit_approx_new(task_data_test)

        # --- Calculate beta variance and accuracy ---
        result_test, acc_test, _ = elaopt.func_ELA(individual=individual, task_data_train=task_data_test_original)
        result_train, acc_train, _ = elaopt.func_ELA(individual=individual, task_data_train=task_data_train_original)

        # --- Calculate local minima graph ---
        graph_train, _ = elaopt.calc_basin_graph(h_train, W_train, task_data_train)
        graph_test, _ = elaopt.calc_basin_graph(h_test, W_test, task_data_test)

        # --- Get indices of local minima ---
        _, train_10 = elaopt.plot_local_min_s1(task_data_train, graph_train)
        _, test_10 = elaopt.plot_local_min_s1(task_data_test, graph_test)

        # --- Calculate Hamming distance (1024-dim vector) ---
        train_1024 = np.zeros(1024)
        test_1024 = np.zeros(1024)
        train_1024[train_10] = 1
        test_1024[test_10] = 1
        hamming_distances = np.sum(train_1024 != test_1024)

        # --- Append results to lists ---
        ham_list.append(hamming_distances)
        acc_list.append(acc_train)
        beta_list.append(result_train)
        val_list.append(acc_train + result_train)
        print(f"Iteration {i+1}: Hamming distance = {hamming_distances}, Beta variance = {result_train}, Accuracy = {acc_train}")
        # --- Save results as CSV files ---
        if i % 1 == 0:
            pd.DataFrame(ham_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//hamming_random_s1.csv", index=False)
            pd.DataFrame(acc_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//acc_random_train_s1.csv", index=False)
            pd.DataFrame(beta_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//var_random_train_s1.csv", index=False)
            pd.DataFrame(val_list).to_csv(f"ELAGAopt_result//Analysis_result//random_ROI_selection//val_random_train_s1.csv", index=False)


if __name__ == "__main__":
    # --- Run main with specified seed ---
    seed = 800
    for i in range(1):
        main(seed)


