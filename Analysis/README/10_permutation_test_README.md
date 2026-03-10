# Usage Guide: `10_permutation_test`

This script performs statistical significance testing and visualization of objective function values using permutation tests. It compares the distribution of objective function values (e.g., Ising model fit accuracy + parameter variance) between random ROI selections and ELA/GAopt-selected ROIs, performs t-test, Mann-Whitney U test, permutation test, calculates Cohen's d effect size, and creates visualizations.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`10_permutation_test.py` evaluates whether ELA/GAopt-selected ROI individuals perform significantly better than random ROI selections on objective function metrics. The script:
1. Loads objective function values for both random and GA-optimized ROI selections
2. Performs multiple statistical tests:
   - **Welch's t-test:** Parametric test for difference in means
   - **Mann-Whitney U test:** Non-parametric test for difference in distributions
   - **Permutation test:** Non-parametric resampling test for significance
3. Calculates effect size (Cohen's d) to quantify the magnitude of differences
4. Creates visualizations:
   - Histogram of permutation test null distribution
   - Boxplot and swarmplot comparing the two groups
5. Saves plots as PNG files and prints statistical results

## 1. Inputs
- **Random ROI objective function values**: CSV files containing objective function metrics for randomly selected ROIs. Expected files:
  - `ELAGAopt_result/Analysis_result/random_ROI_selection/acc_random_train_s1.csv` — Ising model fit accuracy for random selections
  - `ELAGAopt_result/Analysis_result/random_ROI_selection/var_random_train_s1.csv` — Parameter variance for random selections
- **ELA/GAopt objective function values**: CSV files containing objective function metrics for GA-optimized selections. Expected files:
  - `ELAGAopt_result/Analysis_result/objective_function/acc_opt_train_s1.csv` — Ising model fit accuracy for GA selections
  - `ELAGAopt_result/Analysis_result/objective_function/var_opt_train_s1.csv` — Parameter variance for GA selections

All input files should contain numerical values in a single column format.

## 2. Outputs
Statistical results and visualization plots:

### Statistical Results (printed to console):
- Welch's t-test: t-statistic and p-value
- Mann-Whitney U test: U-statistic and p-value
- Permutation test: observed difference, p-value, and null distribution summary
- Cohen's d: effect size measure

### Visualization Files (saved to `ELAGAopt_result/Analysis_result/objective_function/`):
- `permutation_test_histogram_ham.png` — Histogram of permutation test null distribution with observed difference marked
- `objective_function_boxplot_ham.png` — Boxplot and swarmplot comparing random vs GA-optimized objective function values

## 3. Configuration (script-level variables)

Located in the `main()` function and `__main__` block:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `seed` | int | `100` (in `__main__`) | Random seed for reproducibility of permutation test |
| `n_permutations` | int | `10000` | Number of permutations for the permutation test |
| Random data paths | string | `"ELAGAopt_result//Analysis_result//random_ROI_selection//acc_random_train_s1.csv"` etc. | Paths to random ROI objective function CSV files |
| GA data paths | string | `"ELAGAopt_result//Analysis_result//objective_function//acc_opt_train_s1.csv"` etc. | Paths to GA-optimized objective function CSV files |

## 4. Behavior / Workflow

### Main Workflow:
1. Set random seeds for reproducibility
2. Load objective function values from CSV files:
   - Read random ROI accuracy and variance, combine them (accuracy + variance)
   - Read GA-optimized accuracy and variance, combine them
3. Print descriptive statistics (length, mean, std) for both groups
4. Perform statistical tests:
   - **Welch's t-test:** Tests for significant difference in means (unequal variances)
   - **Mann-Whitney U test:** Non-parametric test for difference in distributions
   - **Permutation test:** 
     - Calculate observed difference in means
     - Pool all data and perform 10,000 random permutations
     - Count how many permutations produce difference >= observed difference
     - Calculate p-value as proportion of extreme permutations
5. Create visualizations:
   - **Permutation histogram:** Shows null distribution with vertical line at observed difference
   - **Boxplot/swarmplot:** Compares distributions with significance bar
6. Calculate Cohen's d effect size
7. Save plots and return p-value

### Key Operations:
- **Objective function combination:** Script combines accuracy and variance (acc + var) as the primary metric
- **Permutation test:** Uses resampling without replacement to create null distribution
- **Visualization:** Uses matplotlib and seaborn for publication-quality plots

## 5. Usage examples

### Basic usage (run with seed 100):
```bash
python Analysis/10_permutation_test.py
```

The script will perform all tests and save plots with default settings.

### Change seed value:
Edit the `__main__` block:
```python
seed = 500  # Change from 100 to 500
p_value = main(seed)
```

### Modify number of permutations:
Edit the `main()` function:
```python
n_permutations = 50000  # Increase from 10000 to 50000 for more precision
```

### Point to different data files:
```python
random_data_acc = np.array(pd.read_csv("path/to/your/random_acc.csv", header=0))
random_data_beta = np.array(pd.read_csv("path/to/your/random_var.csv", header=0))
exp_data_acc = np.array(pd.read_csv("path/to/your/ga_acc.csv", header=0))
exp_data_beta = np.array(pd.read_csv("path/to/your/ga_var.csv", header=0))
```

### Use different objective function metric:
Comment/uncomment lines to use different metrics:
```python
# For Hamming distance instead of acc + var:
random_data = np.array(pd.read_csv("ELAGAopt_result//Analysis_result//objective_function//hamming_norm_random_s1_re_200.csv", header=0))
exp_data = np.array(pd.read_csv("ELAGAopt_result//Analysis_result//objective_function//hamming_norm_opt_s1_re.csv", header=0))
```

## 6. Output details

### Console output example:
```
Random data length : 100, mean :1.234, std :0.567
Experience data length : 100,mean :1.890, std :0.432
Welchのt検定: t値 = 5.4321, p値 = 0.000012
マン・ホイットニーU検定: U値 = 6789.0000, p値 = 0.000034
1.234 1.890 0.656
観測された差: 0.6560
p値: 0.0001
Cohen's d: 1.2345
Seed: 100, p-value: 0.0001
```

### Plot characteristics:
- **Permutation histogram:** Gray bars showing null distribution, black dashed line at observed difference, title shows p-value
- **Boxplot:** Light blue for random ROIs, darker blue for GA-selected ROIs, with swarmplot overlay and significance bar

## 7. Notes & recommendations

- **Permutation test:** Provides exact p-values for small samples and is non-parametric. 10,000 permutations provide good precision (p-value resolution of 0.0001).
- **Multiple testing:** Script performs three different tests (t-test, U-test, permutation) to provide robust statistical evidence. All should agree for strong conclusions.
- **Effect size:** Cohen's d quantifies practical significance:
  - d < 0.2: negligible effect
  - 0.2 ≤ d < 0.5: small effect
  - 0.5 ≤ d < 0.8: medium effect
  - d ≥ 0.8: large effect
- **Objective function:** Default combines accuracy and variance. Modify combination logic if using different metrics.
- **Seed management:** Different seeds may produce slightly different permutation p-values due to random sampling.
- **Computational time:** 10,000 permutations are fast (seconds), but increasing to 100,000+ may take longer.
- **Data assumptions:** Assumes CSV files contain single columns of numerical values. Handles missing data by flattening arrays.

## 8. Troubleshooting

### Issue: FileNotFoundError for CSV files
- **Cause:** Input CSV paths are incorrect or files do not exist
- **Solution:** Verify that previous scripts (07_random_roi_selection.py, 06_ELAGAopt_result_check.py) have been run to generate required CSV files. Check paths match exactly.

### Issue: "ValueError: could not broadcast input array"
- **Cause:** CSV files have different numbers of rows or incompatible shapes
- **Solution:** Ensure all input CSV files have the same number of rows (individuals). Check for empty or malformed CSV files.

### Issue: Permutation test p-value is always 0.0 or 1.0
- **Cause:** Too few permutations or extreme observed difference
- **Solution:** Increase `n_permutations` to 100,000 for better resolution. Check that data distributions are not identical (which would give p=1.0).

### Issue: Plots are not saved or show empty
- **Cause:** Output directory does not exist or matplotlib backend issues
- **Solution:** Create output directory manually:
  ```bash
  mkdir -p ELAGAopt_result/Analysis_result/objective_function
  ```
  Ensure matplotlib is properly configured for saving PNG files.

### Issue: Statistical tests give conflicting results
- **Cause:** Data may not meet assumptions of parametric tests
- **Solution:** Trust non-parametric tests (Mann-Whitney U, permutation) over t-test for non-normal data. Check data distributions visually.

### Issue: Cohen's d calculation gives division by zero
- **Cause:** One group has zero variance (all values identical)
- **Solution:** This indicates perfect consistency in one group. Effect size is infinite, meaning groups are completely separated.

### Issue: Script runs but produces no console output
- **Cause:** Silent failure in data loading or calculation
- **Solution:** Add debug prints:
  ```python
  print("Random data shape:", random_data.shape)
  print("Exp data shape:", exp_data.shape)
  ```
  Check for empty arrays or NaN values.

### Issue: Memory error during permutation test
- **Cause:** Large datasets with many permutations
- **Solution:** Reduce `n_permutations` or process data in smaller chunks. Ensure sufficient RAM for array operations.

### Issue: Plots look distorted or labels missing
- **Cause:** Matplotlib/seaborn version compatibility or figure size issues
- **Solution:** Update plotting libraries or adjust figure parameters:
  ```python
  fig, ax = plt.subplots(figsize=(8, 6))  # Adjust size
  plt.tight_layout()  # Ensure proper spacing
  ```
