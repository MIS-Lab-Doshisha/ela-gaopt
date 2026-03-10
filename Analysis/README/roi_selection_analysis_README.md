# Usage Guide: `roi_selection_analysis.py` 

This module provides utilities to analyze ROI selection results produced by the GA pipeline. It offers functions to load GA selection tables, aggregate selected ROIs, run binomial tests with FDR correction, compute effect sizes (Cohen's h), map ROI indices to atlas labels, identify individuals composed only of significant ROIs, visualize counts by ROI and network, and run Mann–Whitney U tests between two groups.

---

## 1. Overview and prerequisites

- Language: Python 3.x
- Key dependencies: `pandas`, `scipy`, `statsmodels`, `nilearn`, `matplotlib`
- Input assumptions:
  - GA results: CSV files containing individuals (rows = generations or individuals, columns = ROI genes). The code expects the final-generation individual at row index `999` in some workflows.
  - Atlas labels: a plain-text file where each line corresponds to an atlas node label.
  - Selection summary tables: CSV produced by earlier scripts (e.g., `03_selected_roi_count.py`).

---

## 2. Statistical background (formulas)

Binomial test (one-tailed greater-than):

Given number of trials $n$ and expected probability $p_0$, the one-sided p-value for observing at least $k$ successes is

$$
P(X \ge k) = \sum_{i=k}^{n} \binom{n}{i} p_0^{\,i} (1-p_0)^{\,n-i}.
$$

Cohen's h (effect size for proportions):

$$
h = 2\left(\arcsin\sqrt{p_1} - \arcsin\sqrt{p_2}\right),
$$

where $p_1$ is the observed proportion and $p_2$ is the reference proportion; interpretation rules of thumb: small ~0.2, medium ~0.5, large ~0.8.

Benjamini–Hochberg FDR (brief):

Sort p-values $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$. Find the largest k such that

$$
p_{(k)} \le \frac{k}{m} \cdot q
$$

where $q$ is the target FDR (e.g., 0.05). Mark p_{(1)}..p_{(k)} as significant.

Mann–Whitney U test (two-sample rank test):

The U statistic compares ranks between two independent samples. For large sample sizes, the sampling distribution of U can be approximated by a normal distribution to compute p-values. The test is non-parametric and assesses whether values in one group tend to be larger than in the other.

---

## 3. Class: `ROISelectionAnalyzer`

All methods below are instance methods of `ROISelectionAnalyzer`.

### __init__(expected_p, n_trials=100)
- Purpose: Construct analyzer with expected selection probability and number of trials.
- Args:
  - `expected_p` (float): reference selection probability used in binomial tests.
  - `n_trials` (int): number of GA runs/trials (default 100).
- Behavior: stores parameters for later tests.

### load_selection_table(filepath)
- Purpose: Load ROI selection summary table produced by GA post-processing.
- Args: `filepath` (str) path to CSV. Function expects a header row and uses the first column as index.
- Returns: `pandas.DataFrame` with the table content.

### flatten_and_count(df)
- Purpose: Flatten the selection table into a single list of selected ROI labels/indices and count frequencies.
- Args: `df` (DataFrame) selection table where cells contain ROI labels or empty values.
- Returns: `pandas.Series` indexed by region label with counts (sorted descending).
- Notes: Removes empty or null cells before counting.

### binomial_test_and_fdr(data)
- Purpose: Perform binomial tests (one-sided greater) for every ROI count, apply Benjamini–Hochberg FDR correction, and compute Cohen's h effect sizes.
- Args: `data` (iterable or Series) counts per ROI; `self.n_trials` and `self.expected_p` are used as the binomial parameters.
- Returns: `pandas.DataFrame` with columns: `Region`, `Count`, `p-value`, `FDR-corrected p`, `Significant`, `Cohen's h` sorted by `Count` descending.
- Implementation details:
  - p-values computed by `scipy.stats.binomtest(count, n, p=self.expected_p, alternative='greater')`.
  - FDR correction via `statsmodels.stats.multitest.multipletests` with `method='fdr_bh'`.
  - Cohen's h uses arcsin-square-root transform for proportions as above.

### collect_roi_selection_labels(atlas_label_path, ga_result_pattern, output_path, n_individuals=100)
- Purpose: Map GA selection bit-vectors to human-readable atlas labels and aggregate the labels from the final-generation individuals across multiple GA runs.
- Args:
  - `atlas_label_path` (str): path to text file containing labels (one per line).
  - `ga_result_pattern` (str): pattern to read GA CSVs, e.g. `"ELAGAopt_result//GA_result//best_individual//best_ind_{idx}.csv"` where `idx` is formatted with `idx=i+1`.
  - `output_path` (str): path to save aggregated CSV.
  - `n_individuals` (int): number of GA runs to process (default 100).
- Returns: DataFrame `all_df` where each column corresponds to one GA run and contains the selected ROI labels for that run's final individual.
- Notes: The implementation reads row index `999` as the final-generation individual (adjust if your run length differs). Uses `nilearn.datasets.fetch_coords_power_2011()` for atlas coordinate frame (labels file supplies network names).

### find_all_significant_individuals(fdr_csv_path, select_csv_path)
- Purpose: Identify indices of individuals (from a selection matrix) that are composed entirely of ROIs flagged as significant by FDR.
- Args:
  - `fdr_csv_path` (str): path to FDR results CSV containing a `Region` column and `Significant` boolean column.
  - `select_csv_path` (str): path to CSV whose columns/entries list ROI labels for each individual.
- Returns: List of integer indices of individuals composed only of significant ROIs.
- Behavior: Loads both CSVs, builds a set of significant ROI names, iterates individuals, and checks membership of every labeled ROI.

### plot_roi_and_network_counts(atlas_label_path, fdr_csv_path, output_prefix)
- Purpose: Merge FDR-corrected ROI list with Power atlas metadata, compute ROI and network-level counts, and save publication-ready bar plots.
- Args:
  - `atlas_label_path` (str): path to atlas labels file.
  - `fdr_csv_path` (str): FDR results CSV.
  - `output_prefix` (str): prefix for saved files; function saves `"{output_prefix}_count.png"`, `"{output_prefix}_count.svg"`, and `"{output_prefix}_fdr_xyz.csv"`.
- Behavior:
  - Loads Power atlas with `nilearn.datasets.fetch_coords_power_2011()` and reads labels file.
  - Cleans labels (removes suffixes), merges with the FDR results (only `Significant == True`), sorts by `Count`.
  - Computes aggregated counts per network and renders a horizontal bar chart with Arial font, numeric annotations, and both PNG and SVG outputs.
- Notes: Adjust plotting parameters (figure size, font) if needed for other environments.

### mannwhitneyu_test(csv_path, col1="ASD", col2="CTL", alpha=0.05, encoding="latin1")
- Purpose: Perform a two-sample Mann–Whitney U test between two columns in a CSV and return test statistics.
- Args:
  - `csv_path` (str): path to CSV containing at least two numeric columns.
  - `col1`, `col2` (str): column names for group 1 and group 2.
  - `alpha` (float): significance threshold for returning `significant` boolean.
  - `encoding` (str): file encoding used when reading CSV.
- Returns: dict with keys `statistic`, `p_value`, and `significant` (boolean). If column lengths do not match, returns an `error` message and None values.
- Notes: Uses `scipy.stats.mannwhitneyu`. The function currently calls the default test; if you require a specific alternative hypothesis (`'two-sided'`, `'greater'`, `'less'`), modify the `mannwhitneyu` call accordingly.

---

## 4. Usage examples

Load selection table and compute FDR-corrected significance:

```python
from roi_selection_analysis import ROISelectionAnalyzer
import pandas as pd

analyzer = ROISelectionAnalyzer(expected_p=0.15, n_trials=100)
df = analyzer.load_selection_table('selected_roi_table.csv')
counts = analyzer.flatten_and_count(df)
results = analyzer.binomial_test_and_fdr(counts)
results.to_csv('selected_roi_fdr_results.csv', index=False)
```

Map GA bit-vectors to labels and save aggregation:

```python
all_df = analyzer.collect_roi_selection_labels(
    atlas_label_path='power2011_labels.txt',
    ga_result_pattern='ELAGAopt_result//GA_result//best_individual//best_ind_{idx}.csv',
    output_path='selected_roi_labels_all_runs.csv',
    n_individuals=100
)
```

Plot significant ROI counts by network:

```python
analyzer.plot_roi_and_network_counts('power2011_labels.txt', 'selected_roi_fdr_results.csv', 'output/roi_counts')
```

Run group comparison for a ROI metric CSV:

```python
res = analyzer.mannwhitneyu_test('roi_metric.csv', col1='ASD', col2='CTL')
print(res)
```

---

## 5. Practical notes

- Confirm the GA output CSV naming pattern and final-generation row index before using `collect_roi_selection_labels`.
- The FDR procedure expects independent tests; interpret results with domain knowledge about ROI correlations.
- The `binomial_test_and_fdr` method treats counts as successes across `n_trials` independent GA runs — ensure `n_trials` matches how counts were produced.
- When plotting on headless servers, set a non-interactive backend for Matplotlib (e.g., `matplotlib.use('Agg')`) before creating figures.

---

If you want, I can also:
- add a small unit-test script demonstrating each method on synthetic data, or
- generate a Jupyter notebook with step-by-step examples and plots.
