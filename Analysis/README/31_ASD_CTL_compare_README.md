# Usage Guide: `31_ASD_CTL_compare`

This script compares ROI selection results between ASD and CTL groups by evaluating Ising model fit accuracy and parameter variance for each group using ELA optimization results. It processes 100 best individuals from GA results and saves comparison metrics as CSV files.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`31_ASD_CTL_compare.py` evaluates the performance of GA-selected ROI sets on ASD and CTL groups separately. The script:
1. Loads brain activity data for both groups
2. Loads 100 best individuals from GA optimization results
3. For each individual (ROI set), evaluates Ising model fit on ASD and CTL data separately
4. Collects variance, accuracy, and other metrics for both groups
5. Saves comparison results as CSV files

## 1. Inputs
- **Brain activity data** (`pkl_path`): Directory containing binary data files for ASD and CTL groups. Loaded using `elaopt.load_brain_data()` with `group_split=True`.
- **GA results** (`ga_result_path`): Directory containing best individual CSV files from GA optimization. Expected format: `best_ind_1000_all_ROI12_1_{k+4}.0.csv` for k in range(100).

## 2. Outputs
CSV files saved to the specified output directory:
- `var_ASD_CTL.csv` — Parameter variance comparison between ASD and CTL groups
- `acc_ASD_CTL.csv` — Ising model accuracy comparison between ASD and CTL groups
- `num_ASD_CTL.csv` — Number of selected ROIs comparison between ASD and CTL groups
- `val_ASD_CTL.csv` — Combined objective function value (variance + accuracy) comparison

### Output Structure (all CSV files):
- **ASD**: Metrics for ASD group
- **CTL**: Metrics for CTL group
- 100 rows (one per individual)

## 3. Configuration (script-level variables)

Located in the `main()` function:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pkl_path` | string | `"Data//test_data_3//binary_data"` | Directory containing brain activity data files |
| `ga_result_path` | string | `"ELAGAopt_result//GA_result//best_individual//test_data_3"` | Directory containing GA best individual CSV files |
| `output_dir` | string | `"ELAGAopt_result//Analysis_result//ASD_CTL_compare"` | Directory where CSV results are saved |

## 4. Behavior / Workflow

### Main Workflow:
1. Set random seed for reproducibility
2. Load brain activity data for ASD and CTL groups separately
3. Initialize lists to store metrics for both groups
4. For each of 100 individuals:
   - Load individual from CSV file
   - Evaluate on ASD data using `elaopt.func_ELA()`
   - Evaluate on CTL data using `elaopt.func_ELA()`
   - Store variance, accuracy, ROI count, and combined value for both groups
5. Convert results to DataFrames and save as CSV files

### Key Function: `elaopt.func_ELA(individual, task_data_train)`

**Purpose**: Evaluate Ising model fit for a given ROI selection on training data

**Returns**: (variance, accuracy, num_selected_rois)

**Note**: This is the same objective function used in GA optimization

### Key Function: `elaopt.load_brain_data(pkl_path, group_split=True)`

**Purpose**: Load brain activity data and split into ASD/CTL groups

**Returns**: (group1_data, group2_data, _)

**Note**: Group split is based on file organization in the data directory

## 5. Usage examples

### Basic usage (compare ASD vs CTL for GA results):
```bash
python Analysis/31_ASD_CTL_compare.py
```

The script will load data, evaluate all 100 individuals, and save comparison CSV files.

### Change data source:
```python
pkl_path = "Data/your_dataset/binary_data"
ga_result_path = "ELAGAopt_result/GA_result/best_individual/your_dataset"
output_dir = "ELAGAopt_result/Analysis_result/ASD_CTL_compare_your_dataset"
```

### Modify number of individuals to evaluate:
Edit the loop range in `main()`:
```python
for k in range(50):  # Evaluate only first 50 individuals
```

### Add additional metrics:
Modify the evaluation loop to collect more metrics:
```python
# Add correlation or other metrics
corr_g1 = calculate_correlation(individual, task_data_1)
corr_g2 = calculate_correlation(individual, task_data_2)
```

### Change output format:
Save as Excel files instead of CSV:
```python
var_df.to_excel(f"{output_dir}//var_ASD_CTL.xlsx", index=False)
```

## 6. Output details

### Console output example:
```
Total files loaded: group1=45, group2=33

result g1: var=0.123456, acc=0.789012, sum=0.912468, num=12
result g2: var=0.234567, acc=0.678901, sum=0.913468, num=12
...
```

### CSV file structure example (`var_ASD_CTL.csv`):
```
ASD,CTL
0.123456,0.234567
0.345678,0.456789
...
```

### Metrics explanation:
- **Variance (var)**: Parameter variance of the fitted Ising model
- **Accuracy (acc)**: Accuracy of the Ising model fit
- **Number (num)**: Number of selected ROIs in the individual
- **Value (val)**: Combined objective function value (variance + accuracy)

## 7. Notes & recommendations

- **Group assignment**: ASD is group1, CTL is group2 based on data loading order
- **Individual files**: Script expects specific naming pattern for GA result files
- **Evaluation consistency**: Uses same ELA function as GA optimization for fair comparison
- **Random seed**: Set to 1000 for reproducible results
- **Performance**: Evaluating 100 individuals may take time depending on data size
- **Data requirements**: Ensure binary data files are properly formatted and grouped
- **Output directory**: Will be created if it doesn't exist

## 8. Troubleshooting

### Issue: FileNotFoundError for GA result files
- **Cause:** `ga_result_path` is incorrect or GA optimization has not been run
- **Solution:** Verify that best individual CSV files exist and path is correct

### Issue: IndexError in individual loading
- **Cause:** CSV file structure doesn't match expected format or row 999 doesn't exist
- **Solution:** Check that GA result files have at least 1000 rows and correct column structure

### Issue: Empty or incorrect group data
- **Cause:** Data loading issues or incorrect group split
- **Solution:** Verify data directory structure and `elaopt.load_brain_data()` function

### Issue: Memory error during evaluation
- **Cause:** Large datasets loaded into memory
- **Solution:** Process fewer individuals or optimize data loading

### Issue: All metrics are zero or NaN
- **Cause:** Invalid ROI selections or data issues
- **Solution:** Check individual values and ensure ROIs are valid indices

### Issue: Output directory creation fails
- **Cause:** Permission issues or invalid path
- **Solution:** Create directory manually or check write permissions

### Issue: ImportError for elagaopt
- **Cause:** elagaopt module not found or not installed
- **Solution:** Ensure elagaopt is in Python path or install if needed

### Issue: Multiprocessing import unused
- **Cause:** Script imports Pool but doesn't use it
- **Solution:** Remove unused import or implement parallel processing if needed

### Issue: Random seed not affecting results
- **Cause:** Random operations not present in evaluation
- **Solution:** Random seed may not be necessary; remove if not used

### Issue: Inconsistent results across runs
- **Cause:** Non-deterministic operations in ELA function
- **Solution:** Check if ELA function has random components and ensure reproducibility