"""
ROI選択結果の可視化スクリプト
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
------------------------------------
FDR補正済みROIリストとatlas情報から、
ROIごと・ネットワークごとの選択回数を棒グラフで保存します。

Script for visualizing ROI selection results
-------------------------------------------
From the FDR-corrected ROI list and atlas information,
this script saves bar plots of selection counts for each ROI and each network.
"""

from roi_selection_analysis import ROISelectionAnalyzer

def main():
    # --- パス設定 / Path settings ---
    # AtlasのROIラベルファイル / Atlas ROI label file
    # 既存のatlasラベルファイルを使用 / Using existing atlas label file
    #atlas_label_path = "Data//atlas_data//dosenbach160NodeNames.txt"
    atlas_label_path = "Data//atlas_data//power264NodeNames.txt"
    
    # FDR補正済みROIリスト / FDR-corrected ROI list 
    # created by 03_selected_roi_count.py
    fdr_table_path =  "ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv"

    # 出力ファイルのパス / Output file path
    output_path = "ELAGAopt_result//Analysis_result//ROI_visualization//roi_selection"

    # ROISelectionAnalyzerのインスタンス作成 / Create analyzer instance
    analyzer = ROISelectionAnalyzer(expected_p=13/264)

    # ROI・ネットワークごとの選択回数を可視化 / Visualize selection counts for each ROI and network
    analyzer.plot_roi_and_network_counts(
        atlas_label_path=atlas_label_path,
        fdr_csv_path=fdr_table_path,
        output_prefix=output_path.rstrip("/")
    )

if __name__ == "__main__":
    main()