"""
有意ROIのみで構成される個体（列）を検索するスクリプト
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
FDR補正済みROIリストと選択集計表から、
全てのROIが有意となっている個体（列）を抽出します。

Script to search for individuals (columns) composed only of significant ROIs
---------------------------------------------------------------------------
From the FDR-corrected ROI list and selection summary table,
this script extracts individuals (columns) where all ROIs are significant.
"""

from elagaopt import ROISelectionAnalyzer

def main():
    # --- パス設定 / Path settings ---
    # ROI選択集計表 / ROI selection summary table made by 01_roi_selection_count_fdr.py
    # created by 03_selected_roi_count.py
    select_table_path = "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv"

    # FDR補正済みROIリスト / FDR-corrected ROI list made by 01_roi_selection_count_fdr.py
    # created by 03_selected_roi_count.py
    fdr_table_path =  "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv"

    # ROISelectionAnalyzerのインスタンス作成 / Create analyzer instance
    analyzer = ROISelectionAnalyzer(expected_p=15/264, n_trials=66)

    # 有意ROIのみで構成される個体（列）のインデックスを取得 / Get indices of individuals with only significant ROIs
    significant_indices = analyzer.find_all_significant_individuals(fdr_table_path, select_table_path)
    # 結果の表示 / Show results
    if significant_indices:
        print("有意ROIのみで構成される個体（列）のインデックス:")
        print("Indices of individuals (columns) composed only of significant ROIs:")
        for idx in significant_indices:
            print(f"{idx} 試行目は成功 / Trial {idx} is successful")
    else:
        print("有意ROIのみで構成される個体は見つかりませんでした。")
        print("No individuals composed only of significant ROIs were found.")

if __name__ == "__main__":
    main()