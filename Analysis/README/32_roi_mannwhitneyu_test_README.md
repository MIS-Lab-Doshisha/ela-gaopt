# Usage Guide: `32_roi_mannwhitneyu_test`

This script performs group comparison and visualization using Mann-Whitney U test between ASD and CTL groups. It calculates statistical significance, effect size r, and rank-biserial correlation for indicators (e.g., number of local minima), and creates boxplots and countplots to visualize the results.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`32_roi_mannwhitneyu_test.py` compares distributions between ASD and CTL groups using non-parametric statistical tests. The script:
1. Loads comparison data from CSV file (output from `31_ASD_CTL_compare.py`)
2. Performs Mann-Whitney U test using ROISelectionAnalyzer
3. Calculates effect size r and rank-biserial correlation manually
4. Displays statistical results and significance interpretation
5. Creates boxplot with significance bar and countplot for visualization

## 1. Inputs
- **Comparison data** (`csv_path`): CSV file containing ASD and CTL group metrics. Expected format: `num_ASD_CTL.csv` from `31_ASD_CTL_compare.py` with columns "ASD" and "CTL".

## 2. Outputs
- **Console output**: Statistical test results, p-values, effect sizes, and significance interpretation
- **Visualization**: Two plots displayed using matplotlib/seaborn:
  - Boxplot with significance bar showing group comparison
  - Countplot showing value distribution by group

## 3. Configuration (script-level variables)

Located in the `main()` function:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `csv_path` | string | `"ELAGAopt_result//Analysis_result//ASD_CTL_compare//num_ASD_CTL.csv"` | Path to CSV file containing ASD/CTL comparison data |
| `alpha` | float | `0.05` | Significance level for statistical test |
| `encoding` | string | `"latin1"` | File encoding for CSV reading |

## 4. Behavior / Workflow

### Main Workflow:
1. Initialize ROISelectionAnalyzer with expected proportion (12/264 ROIs)
2. Perform Mann-Whitney U test using analyzer.mannwhitneyu_test()
3. Display test results and significance interpretation
4. Load data from CSV file
5. Calculate descriptive statistics (mean, std) for both groups
6. Create visualizations using plot_box_with_significance()
7. Perform manual Mann-Whitney U test and calculate effect sizes

### Key Function: `plot_box_with_significance(exp_data, random_data, title)`

**Purpose**: Create boxplot with significance bar and countplot for group comparison

**Steps**:
1. Create boxplot with ASD/CTL data using seaborn
2. Add significance bar (*) above the plot
3. Display boxplot
4. Create countplot showing distribution of values by group
5. Display countplot

### Key Function: `analyzer.mannwhitneyu_test(csv_path, col1, col2, alpha, encoding)`

**Purpose**: Perform Mann-Whitney U test between two columns in CSV file

**Returns**: Dictionary with statistic, p_value, significant flag, and error message if any

### Manual Calculations:
- **Z value**: (U - mean_U) / std_U where mean_U = n1*n2/2, std_U = sqrt(n1*n2*(n1+n2+1)/12)
- **Effect size r**: z / sqrt(N) where N = n1 + n2
- **Rank-biserial correlation**: 1 - (2*U)/(n1*n2)

## 5. Usage examples

### Basic usage (test and visualize ASD vs CTL comparison):
```bash
python Analysis/32_roi_mannwhitneyu_test.py.py
```

The script will load data, perform statistical tests, display results, and show plots.

### Change data source:
```python
csv_path = "ELAGAopt_result/Analysis_result/ASD_CTL_compare/var_ASD_CTL.csv"
```

### Modify significance level:
```python
result = analyzer.mannwhitneyu_test(csv_path, col1="ASD", col2="CTL", alpha=0.01, encoding="latin1")
```

### Change plot colors:
Edit the `plot_box_with_significance()` function:
```python
sns.boxplot(data=[exp_data, random_data], ax=ax, palette=["red", "blue"])
sns.countplot(x='Value', hue='Group', data=df_combined, palette=["red", "blue"])
```

### Add more statistical tests:
Add additional tests in `main()`:
```python
from scipy.stats import ttest_ind
t_stat, p_t = ttest_ind(ASD_data, CTL_data)
print(f"T-test: t = {t_stat:.4f}, p = {p_t:.4f}")
```

### Save plots instead of displaying:
Modify `plot_box_with_significance()`:
```python
plt.savefig("boxplot.png")
plt.close()
# Similarly for countplot
```

## 6. Output details

### Console output example:
```
Mann–Whitney U test result:
Statistic (U): 1234.5
P value: 0.0123

P value (0.0123) is less than the significance level (0.05), so we reject the null hypothesis.
→ There is a statistically significant difference between the two groups.

ASD Group and CTL Group data:
Mean: 12.34 11.56
Std: 2.34 2.78

Mann–Whitney U test: U = 1234.5000, p = 0.0123
Effect size r = 0.2345 (r = Z/√N)
Rank-Biserial Correlation: 0.3456
```

### Plot outputs:
- **Boxplot**: Shows median, quartiles, and outliers for both groups with significance bar
- **Countplot**: Shows frequency distribution of values for each group

### Statistical measures:
- **Mann-Whitney U**: Non-parametric test statistic
- **P-value**: Probability under null hypothesis
- **Effect size r**: Standardized effect size (0.1=small, 0.3=medium, 0.5=large)
- **Rank-biserial correlation**: Measure of association between groups and ordinal variable

## 7. Notes & recommendations

- **Non-parametric test**: Mann-Whitney U is used for non-normally distributed data
- **Effect size interpretation**: r values: small (0.1), medium (0.3), large (0.5)
- **Significance bar**: Always shown regardless of actual significance (for demonstration)
- **Data encoding**: Uses latin1 encoding for CSV files
- **Expected proportion**: Set to 12/264 ROIs for analyzer initialization
- **Visualization**: Requires matplotlib and seaborn for plotting
- **Manual vs analyzer**: Script performs both analyzer-based and manual calculations
- **Group labels**: ASD and CTL are hardcoded in plot labels

## 8. Troubleshooting

### Issue: FileNotFoundError for CSV file
- **Cause:** `csv_path` is incorrect or `31_ASD_CTL_compare.py` has not been run
- **Solution:** Verify CSV file exists and path is correct

### Issue: Encoding error when reading CSV
- **Cause:** File encoding doesn't match "latin1"
- **Solution:** Try different encoding: `encoding="utf-8"` or `encoding="cp1252"`

### Issue: No module named 'elagaopt'
- **Cause:** elagaopt module not in path
- **Solution:** Ensure elagaopt is installed or in Python path

### Issue: ROISelectionAnalyzer error
- **Cause:** Analyzer initialization or method issues
- **Solution:** Check elagaopt documentation or use manual calculations only

### Issue: Plot display issues
- **Cause:** Matplotlib backend issues or no display available
- **Solution:** Use `plt.savefig()` to save plots instead of `plt.show()`

### Issue: Division by zero in effect size calculation
- **Cause:** Sample size N = 0
- **Solution:** Check that data arrays are not empty

### Issue: Invalid values in data
- **Cause:** NaN or infinite values in CSV
- **Solution:** Clean data or add error checking before statistical tests

### Issue: Significance bar always shown
- **Cause:** Hardcoded in plot function
- **Solution:** Modify to show only when significant: `if result["significant"]:`

### Issue: Color palette issues
- **Cause:** Palette names not recognized
- **Solution:** Use valid seaborn palette names or hex colors

### Issue: Memory error with large datasets
- **Cause:** Loading large CSV files
- **Solution:** Process data in chunks or optimize memory usage

### Issue: Inconsistent results between analyzer and manual calculation
- **Cause:** Different calculation methods or parameters
- **Solution:** Verify calculation formulas and ensure same data is used