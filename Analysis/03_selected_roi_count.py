"""
ROI選択頻度集計＆有意性検定スクリプト 
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
AtlasのROIラベルとGA最適化結果から
1. 各個体で選択されたROIラベルの集計表を作成
2. 各ROIの選択頻度に対して二項検定＋FDR補正を実施

Script for ROI selection frequency counting & significance testing
-----------------------------------------------------------------
From atlas ROI labels and GA optimization results:
1. Create a summary table of selected ROI labels for each individual
2. Perform binomial test + FDR correction for selection frequency of each ROI
"""

from roi_selection_analysis import ROISelectionAnalyzer

def main():
    # --- パス設定 / Path settings ---
    # AtlasのROIラベルファイル / Atlas ROI label file
    # 既存のatlasラベルファイルを使用 / Using existing atlas label file
    # ここでは、Power264のラベルを使用 / Using Power264 labels
    atlas_label_path = "Data//atlas_data//power264NodeNames.txt"

    # GA最適化結果ファイルパターン / GA optimization result file pattern
    # created by 01_main_ELAGAopt.py
    ga_result_path = "ELAGAopt_result//GA_result//best_individual//test_data_2//best_ind_1000_all_ROI13_{idx}.0.csv"

    # 集計表出力先 / Output path for selection summary table
    selection_table_path = "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv"

    # 有意性検定結果出力先 / Output path for significance test result
    fdr_table_path = "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv"

    # --- ROI選択頻度集計と有意性検定の実行 / Execute ROI selection frequency counting and significance testing ---
    # ROISelectionAnalyzerのインスタンス作成
    # n_trials: 個体数 / number of individuals
    # expected_p: 期待されるROI選択確率 / expected probability of ROI selection
    analyzer = ROISelectionAnalyzer(n_trials=100, expected_p=13/264)

    # 1. ROI選択ラベル集計 / Collect ROI selection labels
    print("ROI選択ラベル集計を実行中... / Collecting ROI selection labels...")
    all_df = analyzer.collect_roi_selection_labels(
        atlas_label_path=atlas_label_path,
        ga_result_pattern=ga_result_path,
        output_path=selection_table_path,
        n_individuals=100
    )
    print("ROI選択ラベル集計 完了 / ROI selection label collection completed")

    # 2. 有意性検定（FDR補正）/ Significance test (with FDR correction)
    print("有意性検定（FDR補正）を実行中... / Performing significance test (FDR correction)...")
    df = analyzer.load_selection_table(selection_table_path)
    data = analyzer.flatten_and_count(df)
    results_df = analyzer.binomial_test_and_fdr(data)
    results_df.to_csv(fdr_table_path)
    print("有意性検定 完了 / Significance test completed")
    print(results_df)

if __name__ == "__main__":
    main()