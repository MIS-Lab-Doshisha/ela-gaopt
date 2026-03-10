# Usage Guide: `06_ELAGAopt_result_check`

This script evaluates and visualizes the best individuals selected by the GA (Genetic Algorithm) using the Ising model. It calculates parameter variance, model fit accuracy, and the number of local minima, then saves the results to CSV files.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`06_ELAGAopt_result_check.py` loads the best ROI-selected individuals from GA results and evaluates them using the Ising model. It computes three key metrics:
- **Variance (var):** Variance of individual parameters in the Ising model
- **Accuracy (acc):** Ising model fit accuracy (how well the model explains the task data)
- **Number of local minima (num):** Count of local stable states in the energy landscape

Results are saved as CSV files for further analysis and visualization.

## 1. Inputs
- **GA result directory** (`ga_result_path` in script): Directory containing best individual CSV files (e.g., `ELAGAopt_result/GA_result/best_individual/test_data_1/`). Expected format: `best_ind_var_1000_{k+2}.0.csv` where k is the individual index.
- **Task data** (`pkl_path` in script): Pickle file(s) containing preprocessed brain activity data (e.g., `Data/test_data_1/test`). Must be compatible with `elaopt.load_brain_data()`.

## 2. Outputs
CSV files saved to the specified `output_path`:
- `var_opt_{prefix}.csv` — Individual parameter variance for each best individual
- `acc_opt_{prefix}.csv` — Ising model fit accuracy for each best individual
- `num_opt_{prefix}.csv` — Number of local minima for each best individual
- `val_opt_{prefix}.csv` — Sum of variance and accuracy for each individual

All files are saved to: `ELAGAopt_result/Analysis_result/objective_function/` (by default)

## 3. Configuration (script-level variables)

Located in the `main()` function:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pkl_path` | string | `"Data/test_data_1/test"` | Path to pickle file(s) containing task data |
| `ga_result_path` | string | `"ELAGAopt_result/GA_result/best_individual/test_data_1"` | Directory containing GA-selected best individual CSV files |
| `output_path` | string | `"ELAGAopt_result/Analysis_result/objective_function/"` | Directory where output CSV files are saved |
| `n_individuals` | int | `100` | Number of best individuals to evaluate |
| `all_or_first` | string | `"no"` | `"all"` evaluates all rows in individual CSV; any other value evaluates only the last generation |

## 4. Behavior / Workflow

### Main Workflow:
1. Set random seed for reproducibility
2. Load task data from pickle file using `elaopt.load_brain_data()`
3. Depending on `all_or_first`:
   - **"all":** Call `all_evaluate_individuals()` — evaluates all rows in each individual CSV (all generations)
   - **Other:** Call `evaluate_individuals()` — evaluates only the last generation of each individual
4. For each individual:
   - Load the best individual CSV file
   - Extract the individual (last row for standard evaluation)
   - Evaluate using Ising model via `elaopt.func_ELA()` to compute variance, accuracy, and number of local minima
   - Store results
5. Convert results to DataFrames and save as CSV files

### Caching (in `all_evaluate_individuals`):
- The `all_evaluate_individuals()` function uses memoization to avoid recalculating the same individual
- Converts individuals to tuples for use as dictionary keys
- Prints `"Cached result used"` for previously computed individuals

## 5. Usage examples

### Basic usage (evaluate last generation only):
```bash
python Analysis/06_ELAGAopt_result_check.py
```

### Evaluate all generations:
Edit the script and change the line:
```python
all_or_first = "all"  # Instead of "no"
```
Then run:
```bash
python Analysis/06_ELAGAopt_result_check.py
```

### Modify paths before running:
```python
def main():
    pkl_path = "Data/your_data_folder/test"
    ga_result_path = "ELAGAopt_result/GA_result/best_individual/your_data_folder"
    output_path = "ELAGAopt_result/Analysis_result/objective_function/"
    n_individuals = 50  # Evaluate 50 individuals
    all_or_first = "no" # Evaluate last generation only
```

## 6. Output details

### Console output example:
```
Iter 0, Row 0: Calculating...
0.456 0.789 1.245
Iter 0, Row 1: Calculating...
0.432 0.801 1.233
...
```

### CSV file structure:
Each output CSV has one row per individual with columns:
- Column 0: Numerical index or metric value

Example (`var_opt_test_cr.csv`):
```
0
0.456
0.432
0.471
...
```

## 7. Notes & recommendations

- **Ising model evaluation** is computationally intensive. For large numbers of individuals or large datasets, this script may take considerable time.
- **Memoization** in `all_evaluate_individuals()` helps avoid redundant calculations when the same individual appears in multiple generations.
- **GPU acceleration:** The `func_ELA()` call in `all_evaluate_individuals()` uses `use_gpu=False` by default. Change to `use_gpu=True` for faster computation if a GPU is available.
- **Random seed:** The script sets `random.seed(1000)` for reproducibility. Modify if you need different random behavior.
- **File naming convention:** Input best individual files must follow the naming pattern `best_ind_var_1000_{k+2}.0.csv` to be discovered correctly.
- The prefix parameter (e.g., `prefix="test_cr"`) is appended to output file names for easier organization and tracking of different experiments.

## 8. Troubleshooting

### Issue: FileNotFoundError for individual CSV files
- **Cause:** `pkl_path` or `ga_result_path` is incorrect, or best individual files do not exist
- **Solution:** Verify paths point to correct directories and confirm that `01_main_ELAGAopt.py` has been run to generate GA results

### Issue: Script runs but produces no output files
- **Cause:** `output_path` directory does not exist or is not writable
- **Solution:** Create the output directories manually:
  ```bash
  mkdir -p ELAGAopt_result/Analysis_result/objective_function/var
  mkdir -p ELAGAopt_result/Analysis_result/objective_function/acc
  mkdir -p ELAGAopt_result/Analysis_result/objective_function/num
  ```

### Issue: ImportError for `elagaopt`
- **Cause:** The `elagaopt` package is not installed or not in Python path
- **Solution:** Ensure the `Analysis/elagaopt/` directory exists and is importable (check `__init__.py` is present)

### Issue: Accuracy or variance values are NaN or unexpected
- **Cause:** Task data may be incompatible with individuals, or data loading failed
- **Solution:** Verify that the pickle files in `pkl_path` contain valid brain activity data in the expected format

### Issue: Script runs very slowly
- **Cause:** Evaluating many individuals or large individuals with CPU-only computation
- **Solution:** 
  - Reduce `n_individuals` parameter
  - Use `all_or_first = "no"` instead of `"all"` to evaluate only the final generation
  - Consider enabling GPU acceleration if available: change `use_gpu=False` to `use_gpu=True`
