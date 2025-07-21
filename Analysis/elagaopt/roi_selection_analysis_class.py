import pandas as pd
from collections import Counter
from scipy.stats import binomtest
from statsmodels.stats.multitest import multipletests
from nilearn import datasets
from scipy.stats import mannwhitneyu
from math import asin, sqrt
import matplotlib.pyplot as plt
import matplotlib

class ROISelectionAnalyzer:
    def __init__(self, expected_p, n_trials=100):
        self.n_trials = n_trials
        self.expected_p = expected_p
    
    def load_selection_table(self, filepath):
        """
        ROI選択集計表を読み込む
        Load ROI selection summary table
        03_selected_roi_count.pyで使用 / Used in 03_selected_roi_count.py
        """
        df = pd.read_csv(filepath, header=0, index_col=0)
        return df

    def flatten_and_count(self, df):
        """
        全選択ROIを1列にまとめ、頻度カウント
        Flatten all selected ROIs into one column and count frequencies
        03_selected_roi_count.pyで使用 / Used in 03_selected_roi_count.py
        """
        all_selected = df.values.flatten()
        all_selected = [x for x in all_selected if pd.notnull(x) and x != ""]
        counts = Counter(all_selected)
        data = pd.DataFrame(counts.items(), columns=["Region", "Count"]).sort_values(by="Count", ascending=False)
        data = data.set_index('Region')['Count']
        return data

    def binomial_test_and_fdr(self, data):
        """
        二項検定とFDR補正を実施し、Cohen's hで効果量も計算
        Perform binomial test and FDR correction, also calculate effect size using Cohen's h
        03_selected_roi_count.pyで使用 / Used in 03_selected_roi_count.py
        """
        def cohens_h(p1, p2):
            # arcsin sqrt transformation
            return 2 * (asin(sqrt(p1)) - asin(sqrt(p2)))

        p_values = [binomtest(count, n=self.n_trials, p=self.expected_p, alternative='greater').pvalue for count in data]
        rejects, pvals_corrected, _, _ = multipletests(p_values, method='fdr_bh')
        effect_sizes = [cohens_h(count / self.n_trials, self.expected_p) for count in data]
        results_df = pd.DataFrame({
            'Region': list(data.keys()),
            'Count': list(data.values),
            'p-value': p_values,
            'FDR-corrected p': pvals_corrected,
            'Significant': rejects,
            "Cohen's h": effect_sizes
        }).sort_values('Count', ascending=False)
        return results_df
        
    def collect_roi_selection_labels(self, atlas_label_path, ga_result_pattern, output_path, n_individuals=100):
            """
            AtlasのROIラベルとGA個体選択結果から、各個体で選択されたROIラベルの集計表を作成・保存
            Atlas ROI labels and GA individual selection results are used to create and save a summary table of selected ROI labels for each individual.
            03_selected_roi_count.pyで使用 / Used in 03_selected_roi_count.py
            """
            # Power atlas (2011) のROI座標情報を取得
            dataset = datasets.fetch_coords_power_2011()
            df = pd.DataFrame(dataset['rois'])

            # ROIラベル（ネットワーク名）を読み込み
            with open(atlas_label_path) as f:
                Node = f.readlines()
            Node_df = pd.Series(Node, name="network_label")
            Node_df = Node_df.str.replace(r'_\D*\n$', '', regex=True)  # ラベル整形

            labels_df = Node_df
            all_df = pd.DataFrame()

            # 各GA個体について、選択されたROIラベルを抽出・集計
            for i in range(n_individuals):
                individual = pd.read_csv(
                    ga_result_pattern.format(idx=i+4),
                    index_col=0, header=0
                )
                individual = individual.iloc[999].values  # 最終世代の個体
                selected_labels = labels_df[[bool(x) for x in individual]]
                all_df = pd.concat([all_df, selected_labels], axis=1)

            all_df.to_csv(output_path)
            return all_df
    
    def find_all_significant_individuals(self, fdr_csv_path, select_csv_path):
        """
        有意ROIのみで構成される個体（ROIセット）のインデックスをリストで返す
        04_selected_roi_search.pyで使用/ Used in 04_selected_roi_search.py
        """
        fdr_df = pd.read_csv(fdr_csv_path)
        select_df = pd.read_csv(select_csv_path, index_col=0)

        # 有意ROI名のセットを作成
        true_df = fdr_df[fdr_df["Significant"] == True]["Region"]
        true_set = set(true_df.str.strip())
        significant_indices = []
        for i, item in enumerate(select_df.items()):
            flag = 0
            item = item[1].dropna()
            for column, item_s in item.items():
                item_s = str(item_s).strip()
                if item_s not in true_set:
                    flag = 1
                    break
            if flag == 0:
                significant_indices.append(i)
        return significant_indices
    
    
    def plot_roi_and_network_counts(self, atlas_label_path, fdr_csv_path, output_prefix):
        """
        有意ROIリストとPower atlas情報をマージし、ROIごと・ネットワークごとの選択回数を棒グラフで保存
        Merge significant ROI list with Power atlas information and save bar plots of selection counts for each ROI and network
        Significant列がTrueのROIのみプロット/ Plot only ROIs where Significant column is True
        05_roi_visualization.pyで使用 / Used in 05_roi_visualization.py

        """
        # Power atlas情報
        dataset = datasets.fetch_coords_power_2011()
        #dataset = datasets.fetch_coords_dosenbach_2010()
        df = pd.DataFrame(dataset['rois'])

        with open(atlas_label_path) as f:
            Node = f.readlines()
        Node_df = pd.Series(Node, name="Label")
        Node_df = Node_df.str.replace(r'_\D*\n$', '', regex=True)
        roi_df = pd.concat([df, Node_df], axis=1)
        roi_df["network"] = roi_df["Label"].str.split("_").str[0]

        # FDR補正済みROIリスト
        fdr_df = pd.read_csv(fdr_csv_path)
        # Significant列がTrueのものだけ抽出
        fdr_df = fdr_df[fdr_df["Significant"] == True]
        grouped_df = pd.merge(fdr_df, roi_df, how='left', left_on='Region', right_on='Label')
        grouped_df = grouped_df.sort_values('Count', ascending=True)  # ← 追加：Countで降順ソート
        grouped_df.to_csv(f"{output_prefix}_fdr_xyz.csv")

        network_counts = grouped_df.groupby('network')['Count'].sum().reset_index()

        # ROIごとの棒グラフ（横向き・Arialフォント）
        matplotlib.rcParams['font.family'] = 'Arial'

        plt.figure(figsize=(16, 12))
        bars = plt.barh(grouped_df['Region'], grouped_df['Count'], color="#8cc5e3", height=0.5)
        for bar in bars:
            xval = bar.get_width()
            plt.text(xval + 1, bar.get_y() + bar.get_height()/2, int(xval), va='center', ha='left', fontname='Arial')
        plt.ylabel('Region', fontname='Arial')
        plt.xlabel('Count', fontname='Arial')
        plt.title('Significant brain regions selected by GA', fontname='Arial')
        plt.yticks(fontname='Arial')
        plt.xticks(fontname='Arial')
        plt.tight_layout()
        plt.savefig(f"{output_prefix}_count.png")
        plt.savefig(f"{output_prefix}_count.svg", format='svg')
        plt.close()
    
    def mannwhitneyu_test(self, csv_path, col1="ASD", col2="CTL", alpha=0.05, encoding="latin1"):
        """
        2群間のマンホイットニーU検定（ウィルコクソン順位和検定）を実行し、結果を返す
        """
        data = pd.read_csv(csv_path, encoding=encoding)
        data_column_1 = data[col1]
        data_column_2 = data[col2]

        if len(data_column_1) != len(data_column_2):
            return {
                "error": "2つの列のデータ数が一致しません。",
                "statistic": None,
                "p_value": None,
                "significant": None
            }
        statistic, p_value = mannwhitneyu(data_column_1, data_column_2)
        significant = p_value < alpha
        return {
            "statistic": statistic,
            "p_value": p_value,
            "significant": significant
        }
