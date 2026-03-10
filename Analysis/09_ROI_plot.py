""" 
選択されたROIの安定性を示すガラス脳プロットを作成するコード / Code to create glass brain plots showing the stability of selected ROIs
----------------------------------------------------
動作確認済み/Tested with Python 3.13.2
----------------------------------------------------
Script for creating glass brain plots to show the stability of selected ROIs
----------------------------------------------------
This script creates glass brain plots to visualize the stability of selected ROIs based on their selection frequency across multiple runs. 
The top 3 most frequently selected ROIs are highlighted with larger markers and numbered annotations. 
The script also generates an interactive 3D plot for detailed exploration of the ROIs.
-----------------------------------------------------
"""

import pandas as pd
import numpy as np
from nilearn import plotting
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# --- データの準備 / Data preparation ---
data = [
    ["occipital 142", 99, -29, -75, 28, "occipital"],
    ["angular gyrus 117", 92, 51, -59, 34, "default"],
    ["post occipital 153", 88, 29, -81, 14, "occipital"],
    ["occipital 139", 83, 29, -73, 29, "occipital"],
    ["dACC 27", 40, 9, 20, 34, "cingulo-opercular"],
    ["post occipital 156", 38, -37, -83, -2, "occipital"],
    ["mid insula 44", 36, 37, -2, -3, "cingulo-opercular"],
    ["aPFC 3", 35, -29, 57, 10, "fronto-parietal"],
    ["vFC 40", 31, -48, 6, 1, "cingulo-opercular"],
    ["aPFC 8", 29, 27, 49, 26, "cingulo-opercular"],
    ["precentral gyrus 67", 28, -54, -22, 22, "sensorimotor"],
    ["precuneus 105", 28, 5, -50, 33, "default"],
    ["frontal 32", 24, 58, 11, 14, "sensorimotor"],
    ["inf temporal 91", 24, -61, -41, -2, "default"],
    ["angular gyrus 102", 21, -41, -47, 29, "cingulo-opercular"],
    ["temporal 82", 18, -41, -37, 16, "sensorimotor"],
    ["med cerebellum 120", 17, -6, -60, -15, "cerebellum"],
    ["post occipital 154", 13, 33, -81, -2, "occipital"]
]

data = [
    ["Visual_155", 96, -14, -91, 31, "Visual"],
    ["Visual_162", 92, 24, -87, 24, "Visual"],
    ["Visual_145", 86, 8, -72, 11, "Visual"],
    ["Visual_149", 85, -24, -91, 19, "Visual"],
    ["Sensory_Somatomotor_Mouth_44", 83, 51, -6, 32, "Sensory"],
    ["Sensory_Somatomotor_Mouth_42", 82, -49, -11, 35, "Sensory"],
    ["Visual_170", 80, 6, -81, 6, "Visual"],
    ["Visual_146", 75, -8, -81, 7, "Visual"],
    ["Sensory_Somatomotor_Mouth_45", 73, -53, -10, 24, "Sensory"],
    ["Visual_167", 72, -3, -81, 21, "Visual"],
    ["Visual_156", 62, 15, -87, 37, "Visual"],
    ["Sensory_Somatomotor_Hand_27", 51, -38, -27, 69, "Sensory"],
    ["Sensory_Somatomotor_Hand_24", 43, -40, -19, 54, "Sensory"],
    ["Sensory_Somatomotor_Hand_23", 40, -23, -30, 72, "Sensory"],
    ["Visual_152", 37, -18, -68, 5, "Visual"],
    ["Sensory_Somatomotor_Hand_46", 26, 66, -8, 25, "Sensory"],
    ["Visual_159", 23, 15, -77, 31, "Visual"],
    ["Sensory_Somatomotor_Hand_34", 21, -21, -31, 61, "Sensory"],
    ["Visual_163", 16, 6, -72, 24, "Visual"],
    ["Visual_157", 15, 29, -77, 25, "Visual"]
]

data = [
    ["Sensory_Somatomotor_Hand_24", 98, -40, -19, 54, "Sensory"],
    ["Sensory_Somatomotor_Hand_27", 98, -38, -27, 69, "Sensory"],
    ["Sensory_Somatomotor_Hand_37", 97, -38, -15, 69, "Sensory"],
    ["Uncertain_142", 93, -12, -95, 13, "Uncertain"],
    ["Uncertain_2", 92, 27, -97, -13, "Uncertain"],
    ["Sensory_Somatomotor_Hand_19", 88, 13, -33, 75, "Sensory"],
    ["Sensory_Somatomotor_Hand_18", 85, -7, -33, 72, "Sensory"],
    ["Sensory_Somatomotor_Hand_34", 82, -21, -31, 61, "Sensory"],
    ["Sensory_Somatomotor_Hand_28", 78, 20, -29, 60, "Sensory"],
    ["Sensory_Somatomotor_Hand_21", 68, 29, -17, 71, "Sensory"],
    ["Sensory_Somatomotor_Hand_36", 66, 42, -20, 55, "Sensory"],
    ["Sensory_Somatomotor_Hand_23", 62, -23, -30, 72, "Sensory"],
    ["Sensory_Somatomotor_Hand_31", 49, 10, -17, 74, "Sensory"],
    ["Sensory_Somatomotor_Hand_35", 31, -13, -17, 75, "Sensory"]
]

data = [
    ["Visual_145", 100, 8, -72, 11, "Visual"],
    ["Visual_146", 99, -8, -81, 7, "Visual"],
    ["Visual_170", 99, 6, -81, 21, "Visual"],
    ["Visual_167", 85, -3, -81, 21, "Visual"],
    ["Visual_152", 77, -18, -68, 5, "Visual"],
    ["Visual_163", 73, 6, -72, 24, "Visual"],
    ["Visual_151", 64, -15, -72, -8, "Visual"],
    ["Visual_148", 54, 20, -66, 2, "Visual"],
    ["Visual_156", 51, 15, -87, 37, "Visual"],
    ["Visual_155", 45, -14, -91, 31, "Visual"],
    ["Visual_162", 43, 24, -87, 24, "Visual"],
    ["Visual_149", 34, -24, -91, 19, "Visual"],
    ["Visual_159", 21, 15, -77, 31, "Visual"],
    ["Visual_160", 15, -16, -52, -1, "Visual"],
    ["DefaultMode_86", 12, -44, -65, 35, "Default"],
    ["Visual_150", 11, 27, -59, -9, "Visual"]
]

data = [
    ["Visual_167", 99, -3, -81, 21, "Visual"],
    ["Visual_170", 98, 6, -81, 6, "Visual"],
    ["Visual_145", 96, 8, -72, 11, "Visual"],
    ["Visual_146", 96, -8, -81, 7, "Visual"],
    ["Visual_149", 76, -24, -91, 19, "Visual"],
    ["Visual_155", 73, -14, -91, 31, "Visual"],
    ["Visual_163", 61, 6, -72, 24, "Visual"],
    ["Visual_152", 58, -18, -68, 5, "Visual"],
    ["Visual_156", 57, 15, -87, 37, "Visual"],
    ["Visual_148", 36, 20, -66, 2, "Visual"],
    ["Visual_171", 32, -26, -90, 3, "Visual"],
    ["Visual_151", 23, -15, -72, -8, "Visual"],
    ["Visual_160", 23, -16, -52, -1, "Visual"],
    ["Visual_162", 22, 24, -87, 24, "Visual"],
    ["Visual_159", 17, 15, -77, 31, "Visual"],
    ["DefaultMode_121", 14, 13, 30, 59, "Default"],
    ["Visual_172", 14, -33, -79, -13, "Visual"],
    ["Visual_147", 13, -28, -79, 19, "Visual"],
    ["DefaultMode_99", 13, -16, 29, 53, "Default"],
    ["Visual_150", 13, 27, -59, -9, "Visual"],
    ["Visual_169", 11, 37, -84, 13, "Visual"],
    ["DefaultMode_86", 11, -44, -65, 35, "Default"]
]

# --- データフレームの作成 / Create DataFrame ---
df = pd.DataFrame(data, columns=["Region", "Count", "x", "y", "z", "Network"])

# --- 上位3つのROIを特定 / Identify top 3 ROIs ---
top3_df = df.nlargest(3, 'Count')    # Count列で上位3つを抽出 / Extract top 3 based on 'Count' column
top3_indices = top3_df.index         # 上位3つのインデックスを取得 / Get indices of top 3

# --- カラースキームの設定 / Set color scheme ---
network_colors = {
    "occipital": "#e41a1c",          # 赤 / Red
    "default": "#377eb8",            # 青 / Blue
    "cingulo-opercular": "#4daf4a",  # 緑 / Green
    "fronto-parietal": "#ff7f00",    # オレンジ / Orange
    "sensorimotor": "#dede00",       # 黄色 / Yellow
    "cerebellum": "#984ea3"          # 紫 / Purple
}
network_colors = {
    "Visual": "#e41a1c",   # 赤 / Red
    "Sensory": "#377eb8",  # 青 / Blue
}
network_colors = {
    "Sensory": "#377eb8",    # 青 / Blue
    "Uncertain": "#666666",  # ダークグレー（識別しやすい濃いグレー）/ Dark gray (distinct and easily identifiable)
}
network_colors = {
    "Visual": "#e41a1c",   # 赤 / Red
    "Default": "#377eb8",  # 青 / Blue
}

# --- ネットワークごとに色を割り当てる / Assign colors based on network ---
df['color'] = df['Network'].map(network_colors)

# --- 静止画プロット（論文掲載用） ---
fig = plt.figure(figsize=(12, 8))

# --- ガラス脳プロットの作成 / Create glass brain plot ---
display = plotting.plot_glass_brain(
    None, 
    display_mode='ortho', 
    figure=fig,
    title="ROI Selection Stability (Numbered: Top 3)"
)

# --- ネットワークごとにROIをプロット / Plot ROIs by network ---
for network, color in network_colors.items():               # ネットワークごとにループ / Loop through each network
    subset = df[df['Network'] == network]                   # ネットワークに属するROIのサブセットを抽出 / Extract subset of ROIs belonging to the network
    if subset.empty: continue                               # サブセットが空の場合はスキップ / Skip if subset is empty
    normal_subset = subset[~subset.index.isin(top3_indices)]# 上位3つを除いたサブセット / Subset excluding the top 3
    if not normal_subset.empty:                             # 上位3つを除いたROIを描画（通常サイズ、丸のまま） / Plot ROIs excluding the top 3 (normal size, circular)
        # --- ガラス脳プロットにマーカーを追加 / Add markers to glass brain plot ---
        display.add_markers(                                
            marker_coords=normal_subset[['x', 'y', 'z']].values,
            marker_color=color,
            marker_size=normal_subset['Count'].values * 10,
            marker='o', alpha=0.6
        )
    # --- 上位3つを描画（特大サイズ、丸のまま） / Plot top 3 (extra large size, circular) ---
    top_subset = subset[subset.index.isin(top3_indices)]    # 上位3つのサブセット / Subset of top 3
    if not top_subset.empty:                                # 上位3つが存在する場合に描画 / Plot if top 3 exists
        # --- ガラス脳プロットにマーカーを追加 / Add markers to glass brain plot ---
        display.add_markers(
            marker_coords=top_subset[['x', 'y', 'z']].values,
            marker_color=color,
            marker_size=top_subset['Count'].values * 10.0, # 数字を入れるためかなり大きく
            marker='o', alpha=1.0 # くっきり
        )

# --- 上位3つのROIに番号を追加 / Add numbers to top 3 ROIs ---
# matplotlibのマーカーとして "$1$" のようなTeX形式文字を使うと数字を描画できる / Using TeX-style markers like "$1$" allows us to draw numbers as markers in matplotlib
for rank, (idx, row) in enumerate(top3_df.iterrows(), 1):   # 上位3つをループ / Loop through top 3
    coords = np.array([[row['x'], row['y'], row['z']]])     # ROIの座標 / Coordinates of the ROI
    # --- ガラス脳プロットにマーカーを追加 / Add markers to glass brain plot ---
    display.add_markers(
        marker_coords=coords,   
        marker_color='white',  # 文字色 / Text color
        marker_size=120,       # 文字サイズ（※add_markersでの文字サイズ感度は他と異なるため大きめに指定）/ Text size (needs to be larger due to different sensitivity in add_markers)
        marker=f"${rank}$",    # ここで数字を指定 / Specify the number here
        alpha=1.0
    )

# --- 凡例の作成 / Create legend ---
legend_elements = [Line2D([0], [0], marker='o', color='w', 
                          label=net, markerfacecolor=clr, markersize=10) 
                   for net, clr in network_colors.items()]                  # ネットワークごとに凡例要素を作成 / Create legend elements for each network
# --- 凡例の追加 / Add legend ---
plt.legend(handles=legend_elements, 
           loc='upper left', 
           bbox_to_anchor=(1.0, 1.0), 
           title="Functional Networks",
           borderaxespad=0.)

text_str = "Top 3 Regions (Numbered):\n" + "-"*30 + "\n"            # テキストの初期部分 / Initial part of the text
for i, (idx, row) in enumerate(top3_df.iterrows(), 1):              # 上位3つをループ / Loop through top 3
    text_str += f"{i}. {row['Region']} (Count: {row['Count']})\n"   # テキストにROI名とCountを追加 / Add ROI name and Count to the text

# --- テキストボックスの追加 / Add text box ---
plt.text(1.02, 0.2, text_str, transform=plt.gca().transAxes,    
         fontsize=12, verticalalignment='center', 
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0', alpha=1.0, edgecolor='gray'))

# --- プロットの保存 / Save the plot ---
plt.savefig('ELAGAopt//Analysis_result//ROI_plot//color_coded_brain_map_numbered_s4.png', dpi=300, bbox_inches='tight')
plt.savefig('ELAGAopt//Analysis_result//ROI_plot//color_coded_brain_map_numbered_s4.svg', dpi=300, bbox_inches='tight')

print("静止画 'color_coded_brain_map_numbered_s4.png' と 'color_coded_brain_map_numbered_s4.svg' を保存しました。")


