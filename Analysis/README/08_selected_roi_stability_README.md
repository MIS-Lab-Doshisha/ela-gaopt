# Usage Guide: `07_selected_roi_stability.py` (English)

This script evaluates the stability of ROI selections across GA runs and bootstrapped or repeated experiments. It computes how consistently each ROI is selected, produces stability summaries and plots, and writes aggregated results for downstream analysis. The structure below follows the style used by other Analysis READMEs in this repository (inputs → outputs → configuration → workflow → execution → notes).

---

## Overview

- Entry script: `07_selected_roi_stability.py`
- Purpose: quantify and visualize the stability (consistency) of selected ROIs across multiple GA runs, seeds, or cross-validation folds. Stability is usually reported as selection frequency per ROI and summarized with ranking, heatmaps, and optional thresholding.
- Typical use-case: post-hoc analysis of GA outputs to identify ROIs that are repeatedly selected (robust features) vs. ROIs selected only occasionally (unstable features).

---

## 1. Input Data Requirements

The script expects selection summaries saved by earlier steps of the pipeline. Typical inputs include:

A. Selection table(s)
- Path (default in script): `ELAGAopt_result/GA_result/population/` or `ELAGAopt_result/Analysis_result/selected_ROI_count/`.
- Format: CSV or pickled DataFrame where each column or row corresponds to one GA run/individual and entries list selected ROI indices or names.
- Expected structure: each column = one run; cells contain ROI labels (strings) or binary selection vectors (0/1). Missing entries may be empty or NaN.

B. (Optional) Run metadata
- A small CSV listing run identifiers, seeds, and optionally experimental conditions (e.g., dataset name or group).
- Used to group runs and compute group-level stability.

Assumptions:
- ROI labels are consistent across runs (same naming and ordering). The script normalizes whitespace and casing before counting.
- If selection data is a population pickle, the script can extract best individuals (or all individuals) depending on configuration.

---

## 2. Output Data

Typical outputs saved by the script:

- `ELAGAopt_result/Analysis_result/selected_ROI_stability/stability_summary_{runset}.csv` — CSV with per-ROI selection frequency (count and proportion), rank, and optional group-level frequencies.
- `ELAGAopt_result/Analysis_result/selected_ROI_stability/top_ROIs_{runset}.csv` — CSV listing the top-N most stable ROIs.
- Figures saved under `ELAGAopt_result/Analysis_result/selected_ROI_stability/figs/`, for example:
  - `roi_selection_frequency_bar_{runset}.png` — bar plot of selection frequency for all ROIs or top-K ROIs.
  - `roi_selection_heatmap_{runset}.png` — heatmap showing selection across runs (ROIs × runs binary matrix).
- Optional pickled objects containing intermediate matrices (e.g., binary selection matrix) for reproducibility.

All output filenames include an identifying `runset` or timestamp to avoid overwriting previous analyses.

---

## 3. Configuration (values used in the script)

| Variable | Type | Default (in script) | Description |
| :--- | :--- | :--- | :--- |
| `select_table_path` | str | `ELAGAopt_result/Analysis_result/selected_ROI_count/selected_test_data.csv` | Path to aggregated selection table. |
| `output_dir` | str | `ELAGAopt_result/Analysis_result/selected_ROI_stability/` | Directory for writing summary files and figures. |
| `normalize_labels` | bool | True | Strip whitespace and normalize case when matching ROI names. |
| `top_k` | int | 20 | Number of top ROIs to report in separate CSV or plot. |
| `group_by` | str or None | None | Optional metadata column name used to compute group-specific stability. |

Adjust these variables at the top of the script or via CLI options (if implemented) to fit your data layout.

---

## 4. Functionality and algorithm

The script performs the following high-level steps:

1. Load selection tables and optional run metadata.
2. Convert selection representations to a consistent binary matrix M of shape (n_rois × n_runs), where M[i,j] = 1 when ROI i was selected in run j.
3. Compute per-ROI statistics:
   - `count` = sum_j M[i,j]
   - `freq` = count / n_runs
   - `rank` = ordering by `count` or `freq` descending
4. (Optional) Compute group-level frequencies if `group_by` is provided.
5. Create visualizations:
   - Bar plot of `freq` for all or top-K ROIs.
   - Heatmap of M (or subset) to visually inspect patterns across runs.
6. Save results and figures.

Complexity: time O(n_rois × n_runs) for counting and plotting; memory O(n_rois × n_runs) for the binary matrix. This is typically modest (e.g., 264 × several hundred runs).

---

## 5. Statistical considerations

- Stability is measured as simple selection frequency. This is an intuitive and interpretable measure but does not account for chance-level selection. For large hypothesis testing, consider a null model (random selection preserving number of selected ROIs per run) and compute empirical p-values.
- If runs have different numbers of selected ROIs, normalization by `n_runs` is still valid; however, you may also want to compute weighted frequencies or control for selection-size differences.
- When grouping runs (e.g., different datasets or seeds), compare group-level frequencies to highlight condition-specific stable ROIs.

---

## 6. Execution instructions

Run from the project root or the `Analysis` folder. If `07_selected_roi_stability.py` exposes CLI flags, use them; otherwise modify the configuration constants at the top of the script.

Basic usage (no CLI):

```bash
python Analysis/07_selected_roi_stability.py
```

If CLI options exist (example):

```bash
python Analysis/07_selected_roi_stability.py --select-table ELAGAopt_result/Analysis_result/selected_ROI_count/selected_test_data.csv --output-dir ELAGAopt_result/Analysis_result/selected_ROI_stability/ --top-k 30
```

Pre-run checklist:
- Confirm `select_table_path` exists and contains consistent ROI labels or binary vectors.
- Ensure `output_dir` exists or is creatable by the script.

---

## 7. Example output

A sample `stability_summary.csv` row format:

```
ROI,count,freq,rank
ROI_1,98,0.98,1
ROI_2,87,0.87,2
...
```

Console output might include concise summaries such as:

```
Processed 264 ROIs across 100 runs.
Top 5 ROIs: ROI_1 (0.98), ROI_2 (0.87), ROI_25 (0.73), ROI_10 (0.69), ROI_44 (0.66)
Saved summary to ELAGAopt_result/Analysis_result/selected_ROI_stability/stability_summary_2026-02-26.csv
```

---

## 8. Extending the script

- Null-model testing: add a `--null-iterations` argument to generate random selection matrices that preserve per-run selection sizes and compute empirical p-values for frequencies.
- Robustness plots: include cumulative selection frequency plots or rank-frequency (Zipf-like) plots.
- Interactive visualization: export heatmap data to an interactive HTML (Plotly) for easier exploration.

---

## 9. Edge cases and assumptions

- Mixed input formats: the script attempts to detect whether the selection table contains ROI labels or binary selection vectors. If ambiguous, it logs an error and exits.
- Large numbers of runs: if n_runs is extremely large (thousands), consider sampling runs for visualization while still computing exact frequencies.
- Label mismatches: ROI naming inconsistencies will reduce apparent stability. The script performs simple normalization (strip, lower) but not complex remapping; provide a mapping file if labels differ across sources.

---

## 10. References and related scripts

- `03_selected_roi_count.py` — produces aggregated selection counts used as input for stability analysis.
- `04_selected_roi_search.py` — searches for individuals composed only of FDR-significant ROIs (useful after identifying stable ROIs).
- `01_main_ELAGAopt_HCP.py` and `GA_class.py` — the GA pipeline and model-evaluation utilities whose outputs feed this stability check.

---

If you want, I can also:
- add a CLI wrapper (argparse) to `07_selected_roi_stability.py`,
- implement a small unit test that runs the script on a synthetic selection matrix and checks the `stability_summary` is created, or
- produce example plots and attach them to the repository as demonstrations.
