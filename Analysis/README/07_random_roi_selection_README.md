# Usage Guide: `07_random_roi_selection`

This script evaluates GA-selected ROI individuals by comparing local minima patterns between training and test data using the Ising model. It calculates multiple distance metrics (Hamming distance, normalized Hamming distance, and Jaccard distance) to assess differences in local stability patterns, then saves the results to CSV files.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`07_random_roi_selection.py` loads best individuals from GA results and evaluates them on both training and test datasets. For each individual:
1. Extracts features selected by the individual's ROI component
2. Fits an Ising model to both training and test data
3. Computes local minima (stable states) in the energy landscape
4. Calculates comparison metrics between training and test local minima:
   - **Hamming distance:** Raw count of differing local minima states
   - **Normalized Hamming distance:** Hamming distance divided by union size
   - **Jaccard distance:** 1 - (intersection / union) of local minima sets
   - **Intersection count:** Number of common local minima between train and test

Results are incrementally saved to CSV files for further analysis.

## 1. Inputs
- **Training data** (`task_data_train_original`): Pickle file containing binarized training task data (e.g., `Data/test_data_4/Run01/train/train_data_run01.pkl`). Expected format: list or array of binary feature vectors.
- **Test data** (`task_data_test_original`): Pickle file containing binarized test task data (e.g., `Data/test_data_4/Run01/test/test_data_run01.pkl`). Expected format: list or array of binary feature vectors.
- **GA result directory** (`ga_result_path`): Directory containing best individual CSV files (e.g., `ELAGAopt_result/GA_result/best_individual/`). Expected format: `best_ind_{i+1}.csv` where i is the individual index.

## 2. Outputs
CSV files saved to the specified output directories:

### Objective Function Results (saved to `ELAGAopt_result/Analysis_result/objective_function/`):
- `hamming_random_s1_re_{seed}.csv` — Raw Hamming distances between train and test local minima
- `hamming_norm_opt_s1_re_{seed}.csv` — Normalized Hamming distances (0.0 = perfect match, 1.0 = no overlap)
- `jaccard_random_s1_re_{seed}.csv` — Jaccard distances based on set overlap
- `intersection_random_s1_re_{seed}.csv` — Count of common local minima between train and test

### ROI Selection Results (saved to `ELAGAopt_result/Analysis_result/random_ROI_selection/`):
- `roi_random_s1_{seed}.csv` — Binary vectors of ROI selections for each individual
- `acc_opt_train_s1.csv` — Ising model fit accuracy on training data
- `var_opt_train_s1.csv` — Parameter variance on training data
- `val_opt_train_s1.csv` — Sum of accuracy and variance

## 3. Configuration (script-level variables)

Located in the `main()` function and `__main__` block:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `test_data_path` | string | `"Data/test_data_4/Run01/test/test_data_run01.pkl"` | Path to pickle file containing test task data |
| `train_data_path` | string | `"Data/test_data_4/Run01/train/train_data_run01.pkl"` | Path to pickle file containing training task data |
| `ga_result_path` | string | `"ELAGAopt_result/GA_result/best_individual"` | Directory containing GA-selected best individual CSV files |
| `seed` | int | `500` (incremented by 100 per iteration) | Random seed for reproducibility |
| Loop range | int | `range(100)` | Number of individuals to evaluate (100 by default) |

## 4. Behavior / Workflow

### Main Process:
1. Set random seed for reproducibility
2. Load binarized training and test data from pickle files
3. For each of 100 individuals:
   - Load individual from CSV file: `best_ind_{i+1}.csv`
   - Convert individual to boolean array for feature filtering
   - Extract features selected by the individual from both train and test data
   - Concatenate and convert selected features to DataFrames
   - Fit Ising model to both training and test datasets using `fit_approx_new()`
   - Evaluate individual on both datasets using `func_ELA()` to get accuracy and variance
   - Calculate local minima (basin graph) for both datasets using `calc_basin_graph()`
   - Extract local minima indices using `plot_local_min_s1()`
4. Compute distance metrics:
   - **Raw Hamming distance:** Count of differing elements in vectorized local minima representations
   - **Normalized Hamming distance:** `raw_hamming / union_size`
   - **Jaccard distance:** `1.0 - (intersection_size / union_size)`
   - **Intersection count:** Number of common indices between train and test local minima
5. Incrementally save results to CSV files (updated after each individual evaluation)

### Key Operations:
- **Feature extraction:** Uses boolean filtering to select only features (ROIs) included in the individual
- **Ising model fitting:** Uses `fit_approx_new()` to estimate parameters on selected features
- **Local minima comparison:** Converts local minima indices to 32768-dimensional binary vectors and computes Hamming distance

## 5. Usage examples

### Basic usage (evaluate 100 individuals with seed 600):
```bash
python Analysis/07_random_roi_selection.py
```

The script will evaluate 100 individuals and save results with seed value 600 (500 + 100 from the loop).

### Modify seed values:
Edit the script's `__main__` block:
```python
if __name__ == "__main__":
    seed = 1000  # Change starting seed
    for i in range(1): # Number of iterations
        seed += 100
        main(seed)
```

### Change number of individuals to evaluate:
Edit the `main()` function:
```python
for i in range(50):  # Evaluate 50 individuals instead of 100
    individual_path = os.path.join(ga_result_path, f"best_ind_{i+1}.csv")
    # ... rest of the loop
```

### Point to different data:
```python
def main(seed):
    random.seed(seed)
    with open("Data/your_dataset/test/test_data.pkl", "rb") as file:
        task_data_test_original = pickle.load(file)
    with open("Data/your_dataset/train/train_data.pkl", "rb") as file:
        task_data_train_original = pickle.load(file)
    ga_result_path = "ELAGAopt_result/GA_result/best_individual/your_dataset"
    # ... rest of the code
```

## 6. Output details

### Console output example:
```
Train/Test local minima count: 42 / 38
Jaccard Distance: 0.5238, Normalized Hamming: 0.4286
Raw Hamming Distance: 12
Train local minima indices: [0, 3, 5, 7, 12, ...]
Test local minima indices: [1, 4, 6, 8, 15, ...]
```

### CSV file structure examples:

**`hamming_random_s1_re_600.csv`** (raw Hamming distances):
```
0
12
8
15
14
...
```

**`jaccard_random_s1_re_600.csv`** (Jaccard distances):
```
0
0.5238
0.3571
0.6667
0.5833
...
```

**`roi_random_s1_600.csv`** (binary ROI selection vectors):
```
0,1,0,1,0,1,...  (264 columns for all ROIs)
1,0,1,0,1,0,...
0,1,1,0,0,1,...
...
```

**`acc_opt_train_s1.csv`** (accuracy values):
```
0
0.789
0.801
0.756
...
```

## 7. Notes & recommendations

- **Computational complexity:** Evaluating 100 individuals on both train and test datasets with Ising model fitting is computationally intensive. Expect longer runtimes.
- **Local minima calculation:** The script uses 32768-dimensional vectors to represent local minima indices. For larger datasets, adjust the vector size if needed.
- **Incremental saving:** Results are saved after evaluating each individual (due to `if i % 1 == 0` condition), which helps recover progress if the script is interrupted.
- **Seed management:** The seed is incremented by 100 in the loop. Modify this to avoid seed collisions if running multiple times.
- **Data format:** Input pickle files must contain binary data (0s and 1s). Non-binary data will produce incorrect local minima calculations.
- **Memory usage:** Holding training and test data in memory throughout the script requires sufficient RAM. For very large datasets, consider loading data per individual instead.
- **Feature count assumption:** The script assumes 264 ROIs (based on Power atlas). Adjust vector size in `np.zeros(32768)` if using different atlases.

## 8. Troubleshooting

### Issue: FileNotFoundError for pickle files
- **Cause:** Data paths (`test_data_path` or `train_data_path`) are incorrect or files do not exist
- **Solution:** Verify paths point to valid pickle files containing binarized task data. Check paths are relative to the workspace root.

### Issue: FileNotFoundError for individual CSV files
- **Cause:** `ga_result_path` is incorrect or GA results have not been generated
- **Solution:** Confirm that GA results exist in the expected directory and individual files follow naming pattern `best_ind_{i+1}.csv` where i starts from 0.

### Issue: Script runs but produces no output files
- **Cause:** Output directories do not exist or are not writable
- **Solution:** Create output directories manually:
  ```bash
  mkdir -p ELAGAopt_result/Analysis_result/objective_function
  mkdir -p ELAGAopt_result/Analysis_result/random_ROI_selection
  ```

### Issue: "module 'GA_class' has no attribute 'plot_local_min_s1'"
- **Cause:** The GA_class module is missing the `plot_local_min_s1` function or import is incorrect
- **Solution:** Verify that the `GA_class.py` file contains the `plot_local_min_s1` function. Update the import if the class is renamed.

### Issue: All distance metrics are 0.0 or 1.0
- **Cause:** Local minima calculation may have failed, or train/test local minima sets are identical or completely different
- **Solution:** 
  - Print the local minima indices to verify they are computed correctly: `print(train_10, test_10)`
  - Check that task data is properly filtered by the individual
  - Verify Ising model is fitting correctly to the data

### Issue: Memory error or script crashes unexpectedly
- **Cause:** Insufficient memory for holding both train and test data, or vector size is too large
- **Solution:** 
  - Reduce number of individuals evaluated: change `range(100)` to smaller value like `range(10)`
  - Reduce in-memory data size if possible
  - Monitor system resources during execution

### Issue: Accuracy or variance values are unexpected
- **Cause:** Data filtering by individual may be producing unexpected feature selections
- **Solution:** 
  - Add debug print to verify feature count: `print(f"Selected features: {np.sum(filter_array)}")`
  - Verify individual binary vector contains both 0s and 1s
  - Check that task data is in expected format before filtering
