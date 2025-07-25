"""
----------------------------------------------------
Tested with Python 3.13.2
----------------------------------------------------
Script for group comparison and visualization using Mann–Whitney U test
----------------------------------------------------
Performs Mann–Whitney U test, calculates effect size r and rank-biserial correlation for indicators (e.g., number of local minima) between ASD and CTL groups, and visualizes the results.
----------------------------------------------------
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import elagaopt as elaopt
from scipy.stats import mannwhitneyu, norm

def plot_box_with_significance(exp_data, random_data, title="Comparison of Local minimum number"):
    """
    Draw boxplot with significance bar and countplot
    """
    # --- Draw boxplot with significance bar ---
    fig, ax = plt.subplots(figsize=(5, 8))
    sns.boxplot(data=[exp_data, random_data], ax=ax, palette=["lightblue", "lightgreen"])
    ax.set_xticklabels(["ASD Group", "CTL Group"])
    ax.set_title(title)

    y_max = max(np.max(exp_data), np.max(random_data))
    y_min = min(np.min(exp_data), np.min(random_data))
    h = (y_max - y_min) * 0.05
    y = y_max + h
    x1, x2 = 0, 1
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='k')
    ax.text((x1 + x2) / 2, y + h*0.7, "*", ha='center', va='bottom', color='k', fontsize=20)

    plt.tight_layout()
    plt.show()

    # --- Draw countplot ---
    df_combined = pd.DataFrame({
        "Value": np.concatenate([exp_data, random_data]),
        "Group": ["ASD Group"] * len(exp_data) + ["CTL Group"] * len(random_data)
    })
    plt.figure(figsize=(6, 5))
    sns.countplot(x='Value', hue='Group', data=df_combined, palette=["lightblue", "lightgreen"])
    plt.title("Value distribution by group")
    plt.tight_layout()
    plt.show()

def main():
    # --- Path settings ---
    csv_path = "ELAGAopt_result//Analysis_result//ASD_CTL_compare//num_ASD_CTL.csv"
    analyzer = elaopt.ROISelectionAnalyzer(expected_p=12/264)
    result = analyzer.mannwhitneyu_test(csv_path, col1="ASD", col2="CTL", alpha=0.05, encoding="latin1")

    # --- Show test results ---
    if "error" in result and result["error"]:
        print(result["error"])
        return

    print("Mann–Whitney U test result:")
    print(f"Statistic (U): {result['statistic']}")
    print(f"P value: {result['p_value']}")

    if result["significant"]:
        print(f"\nP value ({result['p_value']:.4f}) is less than the significance level (0.05), so we reject the null hypothesis.")
        print("→ There is a statistically significant difference between the two groups.")
    else:
        print(f"\nP value ({result['p_value']:.4f}) is greater than or equal to the significance level (0.05), so we fail to reject the null hypothesis.")
        print("→ There is no statistically significant difference between the two groups.")

    # --- Load data and visualize ---
    df = pd.read_csv(csv_path, encoding="latin1")
    ASD_data = df["ASD"].values
    CTL_data = df["CTL"].values
    print("ASD Group and CTL Group data:")
    print("Mean:", ASD_data.mean(), CTL_data.mean())
    print("Std:", ASD_data.std(), CTL_data.std())
    plot_box_with_significance(ASD_data, CTL_data)

    # --- Mann–Whitney U test & effect size ---
    u_stat, p_mwu = mannwhitneyu(ASD_data, CTL_data, alternative='two-sided')

    # --- Calculate Z value ---
    n1 = len(ASD_data)
    n2 = len(CTL_data)
    mean_U = n1 * n2 / 2
    std_U = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (u_stat - mean_U) / std_U

    # --- Calculate effect size r ---
    N = n1 + n2
    r = z / np.sqrt(N)
    print(f"Mann–Whitney U test: U = {u_stat:.4f}, p = {p_mwu:.4f}")
    print(f"Effect size r = {r:.4f} (r = Z/√N)")

    # --- Calculate rank-biserial correlation ---
    r_rb = 1 - (2 * u_stat) / (n1 * n2)
    print(f"Rank-Biserial Correlation: {r_rb:.4f}")

if __name__ == "__main__":
    main()