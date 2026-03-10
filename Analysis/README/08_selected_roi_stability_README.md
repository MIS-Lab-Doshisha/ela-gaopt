# Usage Guide: `08_selected_roi_stability`

This script analyzes the stability of GA-selected ROIs across multiple trials by computing pairwise distance metrics between individuals. It compares stability metrics between GA-optimized ROI selections and random ROI selections using Hamming distance and Jaccard index, with statistical significance testing via Mann-Whitney U test. Results are saved as CSV matrices and visualized as boxplots.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`08_selected_roi_stability.py` evaluates the stability and consistency of GA-selected ROI selections across 100 individuals/trials. The script:
1. Loads GA-optimized best individuals and random ROI selections from CSV files
2. Computes pairwise stability metrics between all individuals:
   - **Hamming distance:** Number of differing ROI selections between two individuals
   - **Jaccard index:** Proportion of common ROI selections relative to union (intersection / union)
3. Generates distance matrices for both GA-optimized and random selections
4. Creates boxplots comparing stability metrics between the two groups
5. Applies Mann-Whitney U test to assess statistical significance of differences
6. Saves distance matrices as CSV files and plots as PNG/SVG images

## 1. Inputs
- **GA result directory** (`ga_result_path` in script): Directory containing best individual CSV files. Expected format: `best_ind_{idx}.csv` where idx ranges from 1 to n_individuals. Files should contain the best individual for each trial with the last row (index 999) being the final generation individual.
- **Random ROI selection file** (`random_roi_path`): CSV file containing binary vectors of randomly selected ROIs for each individual (e.g., `ELAGAopt_result/Analysis_result/random_ROI_selection/roi_random_s1_600.csv`). Expected format: rows = individuals, columns = ROIs (0s and 1s).
- **Atlas label file** (`atlas_label_path`): Text file containing ROI labels for reference (e.g., `Data/atlas_data/power264NodeNames.txt`). Used for context but not required for computation.

## 2. Outputs
CSV distance matrices and visualization plots:

### Distance Matrices (saved to `ELAGAopt_result/Analysis_result/selected_ROI_stability/`):
- `stability_metrics_s{scenario_num}_hamming_distances.csv` — Pairwise Hamming distances between GA-optimized individuals (100×100 matrix)
- `stability_metrics_s{scenario_num}_jaccard_indices.csv` — Pairwise Jaccard indices between GA-optimized individuals (100×100 matrix)
- `stability_metrics_random_s{scenario_num}_hamming_distances.csv` — Pairwise Hamming distances between random ROI selections (100×100 matrix)
- `stability_metrics_random_s{scenario_num}_jaccard_indices.csv` — Pairwise Jaccard indices between random ROI selections (100×100 matrix)

### Visualization Files:
- `boxplot_Hamming_Distance_s{scenario_num}.png` — Individual boxplot for Hamming distance comparison
- `boxplot_Jaccard_Index_s{scenario_num}.png` — Individual boxplot for Jaccard index comparison
- `boxplot_stability_metrics_summary_s{scenario_num}.png` — Combined boxplot showing both metrics side-by-side
- `.svg` versions of all boxplots for vector graphics editing

## 3. Configuration (script-level variables)

Located in the `main()` function:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `atlas_label_path` | string | `"Data/atlas_data/power264NodeNames.txt"` | Path to atlas ROI labels file (for reference) |
| `ga_result_path` | string | `"ELAGAopt_result/GA_result/best_individual/best_ind_{idx}.csv"` | Path template for GA-selected best individual files |
| `scenario_num` | int | `1` | Scenario identifier appended to output file names |
| `random_roi_path` | string | `"ELAGAopt_result/Analysis_result/random_ROI_selection/roi_random_s1_600.csv"` | Path to random ROI selection results CSV |
| `n_individuals` | int | `100` | Number of individuals/trials to analyze |

## 4. Behavior / Workflow

### Main Workflow:
1. Set up file paths for GA results and random ROI selections
2. Load random ROI selection data from CSV file
3. For each individual (1 to n_individuals):
   - Load best individual CSV file: `best_ind_{idx}.csv`
   - Extract the individual from the final generation (row 999)
   - Remove the first column (index column)
   - Print debug information: selected ROI count and list
   - Concatenate all individuals into a single DataFrame
4. Call `caluculate_stability_metrics()` to compute pairwise distances:
   - For each pair of individuals (i, j):
     - Calculate Hamming distance: sum of differing ROI selections
     - Calculate Jaccard index: intersection / union of selected ROIs
   - Create distance matrices and save as CSV files
   - Print mean Hamming distance and Jaccard index
5. Create visualization boxplots:
   - Extract upper triangle of distance matrices (to avoid double-counting)
   - Create individual boxplots for Hamming distance and Jaccard index
   - Create combined summary boxplot with both metrics
   - Apply Mann-Whitney U test to assess statistical significance
   - Add significance stars (*, **, ***, ****) to plots
6. Save all plots as PNG and SVG files

### Key Functions:

**`caluculate_stability_metrics(individual_all_df, output_path_prefix, scenario_num=1)`:**
- Computes pairwise Hamming distances and Jaccard indices
- Returns DataFrames with distance matrices
- Saves results to CSV files

**`boxplot_comparison(select_df, random_df, prefix, scenario_num=1)`:**
- Creates individual boxplot comparing GA-selected vs random ROI selections
- Applies Mann-Whitney U test with FDR correction
- Computes Cohen's d effect size
- Saves PNG plot

**`boxplot_comparison_summary(select_ham_df, random_ham_df, select_jac_df, random_jac_df, scenario_num=1)`:**
- Creates side-by-side boxplots for both Hamming distance and Jaccard index
- Combines violin plots and boxplots with statistical annotations
- Applies Mann-Whitney U test to both metrics
- Saves PNG and SVG plots

## 5. Usage examples

### Basic usage (analyze 100 individuals with scenario 1):
```bash
python Analysis/08_selected_roi_stability.py
```

### Analyze with different scenario number:
Edit the `main()` function:
```python
scenario_num = 2  # Change from 1 to 2
```

### Analyze different number of individuals:
Edit the `main()` function:
```python
n_individuals = 50  # Analyze 50 individuals instead of 100
```

### Point to different GA results and random ROI data:
```python
ga_result_path = "ELAGAopt_result/GA_result/best_individual/best_ind_{idx}.csv"
random_roi_path = "ELAGAopt_result/Analysis_result/random_ROI_selection/roi_random_s1_700.csv"
```

### Change atlas labels:
```python
atlas_label_path = "Data/atlas_data/dosenbach160NodeNames.txt"
```

## 6. Output details

### Console output example:
```
Processing individual 1/100
Individual data shape: (264,)
Number of selected ROIs: 15
individual data preview: [1 0 1 0 0 1 ...] ...
Selected ROIs for individual 1: [0 2 5 8 12 15 ...]

...

Stability metrics saved.
mean Hamming distance: 156.34
mean Jaccard index: 0.23

Selected ROIs upper triangle data length: 4950
Random ROIs upper triangle data length: 4950
...
Hamming Distance comparison results:
<StatResult> pvalue=1.2e-45, statistic=123456.0

Jaccard Index comparison results:
<StatResult> pvalue=3.4e-38, statistic=234567.0
```

### CSV file structure examples:

**`stability_metrics_s1_hamming_distances.csv`** (100×100 pairwise Hamming distances):
```
0.0,12,8,15,...      (row 0, distances to all individuals)
12,0.0,14,10,...     (row 1)
8,14,0.0,9,...       (row 2)
...
```

**`stability_metrics_s1_jaccard_indices.csv`** (100×100 pairwise Jaccard indices):
```
0.0,0.52,0.68,0.45,...
0.52,0.0,0.41,0.55,...
0.68,0.41,0.0,0.38,...
...
```

### Plot characteristics:
- **Boxplot colors:** Light blue (#8cc5e3) for random ROIs, darker blue (#1a80bb) for GA-selected ROIs
- **Violin plots:** Show distribution density with boxplots inside
- **Statistical annotations:** Stars indicate p-value thresholds:
  - `****` = p < 0.0001
  - `***` = p < 0.001
  - `**` = p < 0.01
  - `*` = p < 0.05
  - `ns` = not significant
- **Significance test:** Mann-Whitney U test with FDR (Benjamini-Hochberg) correction

## 7. Notes & recommendations

- **Pairwise computation:** The script computes all pairwise distances, resulting in an n×n matrix. For 100 individuals, this is 10,000 comparisons. For larger n, computation time increases quadratically.
- **Upper triangle extraction:** When comparing distributions, the script extracts only the upper triangle (excluding diagonal) to avoid double-counting and diagonal zeros. This gives n*(n-1)/2 = 4,950 unique pairwise combinations for 100 individuals.
- **Distance matrix properties:** 
  - Hamming distance is symmetric (distance[i,j] = distance[j,i])
  - Diagonal is zero (distance from individual to itself is 0)
  - Jaccard index is symmetric and ranges from 0 (no overlap) to 1 (identical selection)
- **Statistical testing:** Mann-Whitney U test is non-parametric and suitable for comparing distributions even if not normally distributed. FDR correction prevents false positives when multiple comparisons are made.
- **Cohen's d interpretation:** Effect sizes are printed for each pairwise comparison (Hamming and Jaccard):
  - d < 0.2: negligible
  - 0.2 ≤ d < 0.5: small
  - 0.5 ≤ d < 0.8: medium
  - d ≥ 0.8: large
- **Output prefix:** Use `scenario_num` to organize results from different experimental runs
- **Memory consideration:** Creating 100×100 matrices for each metric uses minimal memory, but plotting operations are more intensive

## 8. Troubleshooting

### Issue: FileNotFoundError for GA result files
- **Cause:** `ga_result_path` format is incorrect or GA results do not exist in the expected directory
- **Solution:** Verify that GA results were generated by `01_main_ELAGAopt.py` and that files follow naming pattern `best_ind_{idx}.csv` where idx starts from 1

### Issue: FileNotFoundError for random ROI file
- **Cause:** `random_roi_path` is incorrect or `07_random_roi_selection.py` has not been run
- **Solution:** Confirm that random ROI results exist. If not, run `python Analysis/07_random_roi_selection.py` first to generate the required file

### Issue: FileNotFoundError for atlas labels
- **Cause:** `atlas_label_path` is incorrect or atlas data file does not exist
- **Solution:** Verify that atlas label file exists in `Data/atlas_data/`. Note: this file is optional and only used for reference, so missing it won't prevent computation

### Issue: "IndexError: index 999 is out of bounds"
- **Cause:** Best individual CSV files have fewer than 1000 rows, so row 999 does not exist
- **Solution:** Change the row index to match your data:
  ```python
  individual = individual_df.iloc[last_row_index].values  # Use last_row_index instead of 999
  ```

### Issue: Script runs but produces no plots
- **Cause:** Output directory does not exist or is not writable
- **Solution:** Create output directory manually:
  ```bash
  mkdir -p ELAGAopt_result/Analysis_result/selected_ROI_stability
  ```

### Issue: "ValueError: could not broadcast input array"
- **Cause:** GA-selected and random ROI DataFrames have different numbers of columns
- **Solution:** 
  - Verify that both GA result files and random ROI file use the same number of ROIs (e.g., 264)
  - Check that individual CSV files have consistent column count across all files

### Issue: All significance bars show "ns" (not significant)
- **Cause:** GA-selected and random ROI selections have very similar stability characteristics
- **Solution:** 
  - Check that GA optimization is producing meaningfully different selections
  - Verify that random ROI selection method is truly random
  - Examine the actual distance values (mean values) to assess practical difference even if not statistically significant

### Issue: "AttributeError: 'DataFrame' object has no attribute 'where'"
- **Cause:** Pandas version incompatibility with the `where()` method syntax
- **Solution:** Update pandas or modify the upper triangle extraction code:
  ```python
  import numpy as np
  mask = np.triu(np.ones_like(select_df, dtype=bool), k=1)
  select_upper = select_df[mask].dropna()
  ```

### Issue: Plots look distorted or labels are overlapping
- **Cause:** Default figure size or font scaling issue
- **Solution:** Modify figure size and font parameters in the plotting functions:
  ```python
  fig, ax = plt.subplots(figsize=(10, 7))  # Increase figure size
  ax.tick_params(labelsize=14)              # Adjust font size
  ```

### Issue: Memory error when processing large number of individuals
- **Cause:** Creating large distance matrices consumes significant memory
- **Solution:** 
  - Reduce number of individuals: change `n_individuals = 100` to smaller value
  - Process individuals in batches instead of all at once
  - Ensure sufficient RAM available on system

### Issue: Cohen's d values are incorrect or very large
- **Cause:** Very small pooled standard deviation, especially when distributions have little variance
- **Solution:** This is expected behavior when comparing very consistent selections. Verify results manually if needed.
