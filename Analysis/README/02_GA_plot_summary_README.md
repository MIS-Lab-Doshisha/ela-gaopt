# Usage Guide: `02_GA_plot_summary.py`

This script visualizes GA optimization histories across multiple runs. It produces plots of the objective function value (|β variance| + Accuracy), Accuracy, and |β variance| across generations, and saves combined summary figures for comparison between multiple GA runs.

## Overview
The script aggregates per-generation histories produced by `01_main_ELAGAopt.py` and creates:
- Single-run convergence plot of the objective function across multiple trials
- Combined summary figure with three panels (objective, β variance, Accuracy)

Outputs are saved under `ELAGAopt_result/Analysis_result/GA_plot/` by default.

---

## 1. Input Data Requirements

### A. Objective, Accuracy, and Variance CSVs
The script reads CSV files produced by the GA pipeline. Default file patterns used in the script:
- Objective function history (per-run): `ELAGAopt_result//GA_result//objective_function//best_fitness_{i}.csv`
- Accuracy history (per-run): `ELAGAopt_result//GA_result//acc//acc_train_1000_{i}.csv`
- β variance history (per-run): `ELAGAopt_result//GA_result//var//var_train_1000_{i}.csv`

`{i}` is a trial identifier (string or integer). The script uses a `trial_list` to specify which runs to include.

### B. Trial List
- **Specification:** Manually specified in the `trial_list` variable.
- **Format:** List of integers/strings representing trial IDs to include in the visualization.
- **Example:** `trial_list = ["1","2","3",...,"100"]` or a subset of runs.

---

## 2. Output Data

### A. Single Objective Plot
- **Path:** `"ELAGAopt_result/Analysis_result/GA_plot/convergence_plot.png"`
- **Content:** Multi-line convergence plot where each line is the best objective value per generation for a single run.

### B. Combined Summary Figure
- **Path(s):**
  - `"ELAGAopt_result/Analysis_result/GA_plot/convergence_all_plot.png"`
  - `"ELAGAopt_result/Analysis_result/GA_plot/convergence_all_plot.svg"`
- **Content:** Top panel: objective histories; bottom-left: β variance histories; bottom-right: Accuracy histories for all runs.

### C. In-Memory DataFrames
- `best_all`, `acc_all`, `var_all`: pandas DataFrames with shape `(num_generations, num_trials)` representing per-generation histories for objective, accuracy, and variance respectively.

---

## 3. Configuration (Global Variables)

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `num` | int | `1` | Number of runs to include when generating combined plots (used for palette selection). |
| `trial_list` | list | See script | List of trial identifiers to load and plot. |
| `bias` | int | `0` | Optional labeling offset for run indices. |
| Input path templates | str | Hardcoded | Patterns for objective/acc/var CSV files (see Section 1). |
| Output directory | str | Hardcoded | `ELAGAopt_result/Analysis_result/GA_plot/` |

---

## 4. Data Processing Workflow

### A. Data Loading
For each trial in `trial_list`:
1. Read the objective CSV and rename its column to `"Objective value (|β variance| + Accuracy)"`.
2. Read accuracy CSV and rename to `"Accuracy"`.
3. Read variance CSV and rename to `"|β variance|"`.
4. Append each DataFrame to `best_list`, `acc_list`, and `var_list` respectively.

### B. Data Aggregation
Concatenate the lists horizontally to form:
- `best_all` (objective histories)
- `acc_all` (accuracy histories)
- `var_all` (variance histories)

Rename columns as `Run{trial_id}` for clarity.

### C. Visualization
1. Plot a simple multi-line objective convergence plot and save as a PNG.
2. Build a combined figure using `matplotlib.gridspec` with three panels (objective, variance, accuracy) and save PNG/SVG.

---

## 5. Plotting Details

- Color palette: Seaborn `viridis` (perceptually uniform).
- Figure sizes: single plot (10×6), combined (12×8).
- Line transparency: `alpha=0.8`.
- Grid: dashed lines, `alpha=0.6`.
- Output resolution: `dpi=300` for PNGs.

---

## 6. Execution Instructions

Run the script from the project root or the `Analysis` folder:

```bash
python Analysis/02_GA_plot_summary.py
```

Pre-run checks:
- Ensure the CSV files exist at the expected paths.
- Confirm `trial_list` matches the file identifiers you intend to include.
- Ensure the output directory exists or create it before running.

---

## 7. Customization and Troubleshooting

- To change runs to plot, edit `trial_list`.
- For headless servers, set Matplotlib backend to `Agg` before importing `pyplot`:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

- If some files are missing, the script will raise `FileNotFoundError`. Verify file names and trial IDs.
- Reduce plotted runs to a subset if plotting all runs is cluttered or slows rendering.

---

## 8. Integration Notes

- This script depends on outputs from `01_main_ELAGAopt.py` (per-run CSV histories).
- Generated figures are suitable for reports and presentations. For further numerical analysis, export `best_all` / `acc_all` / `var_all` to CSV by adding `to_csv()` calls.

---
