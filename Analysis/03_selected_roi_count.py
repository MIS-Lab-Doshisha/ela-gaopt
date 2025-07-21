"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for ROI selection frequency counting & significance testing
----------------------------------------------------
From atlas ROI labels and GA optimization results:
1. Create a summary table of selected ROI labels for each individual
2. Perform binomial test + FDR correction for selection frequency of each ROI
----------------------------------------------------
"""

import elagaopt as elaopt

def main():
    # --- Path settings ---
    # Atlas ROI label file
    # Using existing atlas label file
    # Using Power264 labels
    atlas_label_path = "Data//atlas_data//power264NodeNames.txt"

    # --- GA optimization result file pattern ---
    # created by 01_main_ELAGAopt.py
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_2//best_ind_1000_all_ROI13_{idx}.0.csv"

    # --- Output path for selection summary table ---
    selection_table_path = "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv"

    # --- Output path for significance test result ---
    fdr_table_path = "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv"

    # --- Execute ROI selection frequency counting and significance testing ---
    # Create an instance of ROISelectionAnalyzer
    # n_trials: number of individuals
    # expected_p: expected probability of ROI selection
    analyzer = elaopt.ROISelectionAnalyzer(n_trials=100, expected_p=13/264)

    # --- 1. Collect ROI selection labels ---
    # Collects ROI selection labels from GA optimization results
    print("Collecting ROI selection labels...")
    all_df = analyzer.collect_roi_selection_labels(
        atlas_label_path=atlas_label_path,
        ga_result_pattern=ga_result_path,
        output_path=selection_table_path,
        n_individuals=100
    )
    print("Collecting ROI selection labels completed")

    # --- 2. Perform significance test (with FDR correction) ---
    print("Performing significance test (FDR correction)...")
    df = analyzer.load_selection_table(selection_table_path)
    data = analyzer.flatten_and_count(df)
    results_df = analyzer.binomial_test_and_fdr(data)
    results_df.to_csv(fdr_table_path)
    print("Significance test completed")
    print(results_df)

if __name__ == "__main__":
    main()