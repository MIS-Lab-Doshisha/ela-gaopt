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

from elagaopt import ROISelectionAnalyzer
from matplotlib import pyplot as plt
import pandas as pd

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

    # --- 棒グラフの描画 / Draw bar graph ---
    plt.figure(figsize=(28, 14))
    grouped_df = pd.read_csv(fdr_table_path, header=0)
    bars = plt.bar(grouped_df['Region'], grouped_df['Count'], color='blue',width=0.8)

    # --- 各棒の上に値を表示 / Display values on top of each bar ---
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval+1, int(yval), va='center', ha='center')

    # --- グラフのラベル設定 / Set graph labels ---
    plt.xlabel('Region')
    plt.ylabel('Count')
    plt.title('Brain regions selected by GA')
    plt.xticks(rotation=90)
    plt.tight_layout()

    # --- グラフを保存 / Save the graph ---
    plt.savefig(output_path + "_count_all.png")
    plt.savefig(output_path + "_count_all.svg", format='svg')
    

if __name__ == "__main__":
    main()