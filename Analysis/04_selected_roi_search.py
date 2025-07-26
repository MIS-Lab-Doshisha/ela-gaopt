"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script to search for individuals (columns) composed only of significant ROIs
----------------------------------------------------
From the FDR-corrected ROI list and selection summary table,
this script extracts individuals (columns) where all ROIs are significant.
----------------------------------------------------
"""

import elagaopt as elaopt

def main():
    # --- Path settings ---
    # ROI selection summary table made by 01_roi_selection_count_fdr.py
    # created by 03_selected_roi_count.py
    select_table_path = "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv"

    # FDR-corrected ROI list made by 01_roi_selection_count_fdr.py
    # created by 03_selected_roi_count.py
    fdr_table_path =  "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv"

    # --- Create analyzer instance ---
    analyzer = elaopt.ROISelectionAnalyzer(expected_p=13/264, n_trials=100)

    # --- Get indices of individuals with only significant ROIs ---
    significant_indices = analyzer.find_all_significant_individuals(fdr_table_path, select_table_path)
    
    # --- Show results ---
    if significant_indices:
        print("Indices of individuals (columns) composed only of significant ROIs:")
        for idx in significant_indices:
            print(f"Trial {idx} is successful")
    else:
        print("No individuals composed only of significant ROIs were found.")

if __name__ == "__main__":
    main()