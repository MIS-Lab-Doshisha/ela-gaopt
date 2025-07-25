"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for visualizing ROI selection results
----------------------------------------------------
From the FDR-corrected ROI list and atlas information,
this script saves bar plots of selection counts for each ROI and each network.
----------------------------------------------------
"""

import elagaopt as elaopt

def main():
    # --- Path settings ---
    # Atlas ROI label file
    # Using existing atlas label file
    #atlas_label_path = "Data//atlas_data//dosenbach160NodeNames.txt"
    atlas_label_path = "Data//atlas_data//power264NodeNames.txt"

    # --- FDR-corrected ROI list ---
    # created by 03_selected_roi_count.py
    fdr_table_path =  "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv"

    # --- Output file path ---
    output_path = "ELAGAopt_result//Analysis_result//ROI_visualization//roi_selection"

    # --- Create analyzer instance ---
    analyzer = elaopt.ROISelectionAnalyzer(expected_p=13/264)

    # --- Visualize selection counts for each ROI and network ---
    analyzer.plot_roi_and_network_counts(
        atlas_label_path=atlas_label_path,
        fdr_csv_path=fdr_table_path,
        output_prefix=output_path.rstrip("/")
    )

if __name__ == "__main__":
    main()