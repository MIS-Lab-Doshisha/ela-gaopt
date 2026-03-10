# Usage Guide: `21_local_min_freq_calc`

This script calculates the frequency of local minima for each ROI set selected by GA. For each individual (ROI set), it processes all subjects' brain activity data, fits an Ising model, and computes the frequency distribution of local minima states across subjects, saving the results as a pickle file.

- **Location:** Analysis/
- **Tested with:** Python 3.13.2

## Overview
`21_local_min_freq_calc.py` analyzes the local minima landscape for GA-selected ROI combinations. The script:
1. Loads GA-selected individuals (binary ROI selections)
2. For each individual, extracts the selected ROIs from all subjects' brain data
3. Fits an Ising model to the selected ROI data
4. Calculates the basin graph (local minima structure)
5. For each subject, determines which local minimum their brain state belongs to
6. Computes frequency distributions of local minima across subjects
7. Saves all frequency data as a pickle file for further analysis

## 1. Inputs
- **GA result directory** (`ga_result_path`): Directory containing best individual CSV files. Expected format: `best_ind_1000_all_ROI13_{k+4}.0.csv` where k ranges from 0 to n_individuals-1.
- **Brain activity data** (`pkl_path`): Directory containing pickle files with binarized brain activity data (e.g., `Data/test_data_2/binary_data`). Data should be compatible with `elaopt.load_brain_data()`.

## 2. Outputs
Pickle file saved to the specified output path:
- `freq_ROI13.pkl` — List of DataFrames containing local minima frequency distributions for each individual

### Output Structure:
- **Outer structure**: List with one element per individual
- **Inner structure**: DataFrame with columns `Frequency_1`, `Frequency_2`, etc. (one per subject)
- **Index**: Local minimum state numbers
- **Values**: Frequency of each local minimum state for that subject

## 3. Configuration (script-level variables)

Located in the `main()` function:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pkl_path` | string | `"Data//test_data_2//binary_data"` | Path to directory containing brain activity pickle files |
| `ga_result_path` | string | `"ELAGAopt_result//GA_result//best_individual//test_data_2"` | Directory containing GA-selected individual CSV files |
| `output_path` | string | `"ELAGAopt_result//Analysis_result//local_min_freq_data//freq_ROI13.pkl"` | Path where frequency data pickle file is saved |
| `n_individuals` | int | `100` | Number of individuals to process |

## 4. Behavior / Workflow

### Main Workflow:
1. Set random seed for reproducibility
2. Load all subjects' brain activity data using `elaopt.load_brain_data()`
3. Initialize empty frequency list
4. For each individual (0 to n_individuals-1):
   - Load individual CSV file: `best_ind_1000_all_ROI13_{k+4}.0.csv`
   - Extract the final generation individual (row 999)
   - Remove the first column (index column)
   - Call `func_ELA()` to calculate local minima frequencies
   - Append result to frequency list
   - Print progress message
5. Save the complete frequency list as a pickle file

### Key Function: `func_ELA(individual, task_data_train)`

**Purpose**: Calculate local minima frequency distribution for a single individual

**Steps**:
1. Create boolean mask from individual (ROI selection)
2. Filter each subject's brain data to include only selected ROIs
3. Concatenate all subjects' filtered data into a single DataFrame
4. Fit Ising model parameters (h, W) using `elaopt.fit_approx_new()`
5. Calculate basin graph (local minima structure) using `elaopt.calc_basin_graph()`
6. For each subject:
   - Convert each time point's binary pattern to decimal representation
   - Map each pattern to its corresponding local minimum state
   - Count occurrences of each local minimum state
   - Calculate frequency (count / total_timepoints)
7. Return DataFrame with frequency distributions for all subjects

## 5. Usage examples

### Basic usage (process 100 individuals):
```bash
python Analysis/21_local_min_freq_calc.py
```

The script will process all individuals and save the frequency data to the default pickle file.

### Change number of individuals:
Edit the `main()` function:
```python
n_individuals = 50  # Process 50 individuals instead of 100
```

### Point to different data:
```python
pkl_path = "Data/your_dataset/binary_data"
ga_result_path = "ELAGAopt_result/GA_result/best_individual/your_dataset"
output_path = "ELAGAopt_result/Analysis_result/local_min_freq_data/freq_your_data.pkl"
```

### Change individual file naming pattern:
Edit the file path construction:
```python
individual_path = os.path.join(ga_result_path, f"best_ind_{k+1}.csv")  # Different naming pattern
```

### Modify random seed:
```python
random.seed(42)  # Different seed for reproducibility
```

## 6. Output details

### Console output example:
```
task data shape: (13, 15000)
Processed individual 1/100
task data shape: (13, 15000)
Processed individual 2/100
...
Processed individual 100/100
All frequency data saved.
```

### Pickle file structure:
```python
# Load the pickle file
with open("freq_ROI13.pkl", "rb") as f:
    freq_list = pickle.load(f)

# freq_list is a list of 100 DataFrames (one per individual)
# Each DataFrame has columns like 'Frequency_1', 'Frequency_2', etc.
# Index represents local minimum state numbers
# Values are frequencies (0.0 to 1.0) for each subject
print(freq_list[0].head())
#        Frequency_1  Frequency_2  ...
# Number
# 0       0.45        0.52         ...
# 1       0.32        0.28         ...
# 2       0.23        0.20         ...
```

## 7. Notes & recommendations

- **Computation time**: Ising model fitting and basin graph calculation are computationally intensive. Processing 100 individuals may take significant time.
- **Memory usage**: Loading all subjects' brain data at once requires substantial RAM. Ensure sufficient memory is available.
- **Data format**: Input brain data must be binarized (0/1 values). The script assumes 13 ROIs are selected (based on filename pattern).
- **File naming**: Individual files follow pattern `best_ind_1000_all_ROI13_{k+4}.0.csv`. Adjust the pattern if your files use different naming.
- **Local minima calculation**: The basin graph represents the energy landscape's local minima. Each brain state is mapped to the nearest local minimum.
- **Frequency calculation**: For each subject, frequency is calculated as the proportion of time spent in each local minimum state.
- **Output size**: The pickle file can be large depending on the number of individuals and local minima states.
- **Reproducibility**: Random seed affects any stochastic operations in the Ising model fitting.

## 8. Troubleshooting

### Issue: FileNotFoundError for individual CSV files
- **Cause:** `ga_result_path` is incorrect or GA results do not exist
- **Solution:** Verify that GA results were generated and the path matches the expected directory structure

### Issue: FileNotFoundError for pickle data
- **Cause:** `pkl_path` is incorrect or brain data files do not exist
- **Solution:** Check that binarized brain data exists in the specified directory and is compatible with `elaopt.load_brain_data()`

### Issue: "IndexError: index 999 is out of bounds"
- **Cause:** Individual CSV files have fewer than 1000 rows
- **Solution:** Adjust the row index:
  ```python
  individual = individual_df.iloc[-1].values  # Use last row instead of row 999
  ```

### Issue: Memory error during processing
- **Cause:** Insufficient RAM for loading brain data or processing large datasets
- **Solution:** 
  - Reduce `n_individuals`
  - Process individuals in smaller batches
  - Ensure sufficient system memory

### Issue: Empty frequency DataFrames
- **Cause:** No local minima found or data filtering issues
- **Solution:** 
  - Check that ROI selection contains both 0s and 1s
  - Verify brain data is properly binarized
  - Debug Ising model fitting by checking intermediate outputs

### Issue: "ValueError: could not broadcast input array"
- **Cause:** Mismatch between individual length and brain data dimensions
- **Solution:** Ensure individual vectors match the number of ROIs in the brain data

### Issue: Pickle file not created
- **Cause:** Script crashed before saving or output directory doesn't exist
- **Solution:** Create output directory manually and check for errors in console output

### Issue: Inconsistent results across runs
- **Cause:** Random seed not set or stochastic operations in Ising model
- **Solution:** Ensure `random.seed()` and `np.random.seed()` are set consistently

### Issue: Very slow processing
- **Cause:** Large brain datasets or complex Ising model calculations
- **Solution:** 
  - Reduce dataset size if possible
  - Check for infinite loops in basin graph calculation
  - Monitor system resources during execution

### Issue: ImportError for elagaopt
- **Cause:** elagaopt module not found or incorrectly imported
- **Solution:** Ensure the Analysis/elagaopt/ directory is in the Python path and __init__.py exists
