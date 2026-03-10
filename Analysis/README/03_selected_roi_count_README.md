# Usage Guide: `03_selected_roi_count.py` 

This script aggregates ROI selection labels from GA optimization runs and performs binomial significance testing with FDR correction for ROI selection frequencies.

It builds on `ROISelectionAnalyzer` utilities (see `roi_selection_analysis.py`) and follows a two-step workflow:

1. Collect selected ROI labels from each GA run's final individual and save a summary table.
2. Count selection frequencies across runs, run one-sided binomial tests per ROI, and apply Benjamini–Hochberg FDR correction.

---

## 1. Overview

- Entry point: `main()` in `03_selected_roi_count.py`.
- Uses the `ROISelectionAnalyzer` class to map GA bit-vectors to atlas labels and compute statistics.
- Typical use: run after GA optimizations (outputs from `01_main_ELAGAopt.py`).

---

## 2. Inputs and default paths (as in script)

- Atlas labels file: `Data//atlas_data//power264NodeNames.txt`
- GA result file pattern: `ELAGAopt_result//GA_result//best_individual//best_ind_1000_all_ROI13_{idx}.csv` .
- Aggregated selection table output: `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv`.
- FDR result output: `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv` (currently commented out in script).

Adjust these paths in the script or call parameters before running if your project uses different locations.

---

## 3. Parameters used in `main()`

- `n_individuals=N`: Number of GA runs processed (default in the script). Update to match how many `best_ind_1000_all_ROI13_{idx}.csv` files you have.
- `expected_p=13/264`: Expected ROI selection probability used for binomial tests. In this script the expected probability is set to selecting 13 ROIs out of 264 uniformly.

---

## 4. Detailed workflow (what `main()` does)

1. Instantiate `ROISelectionAnalyzer` with `n_trials=N` and `expected_p=13/264`.
2. Call `collect_roi_selection_labels()` to read each GA `best_ind_1000_all_ROI13_{idx}.csv`, extract the final-generation individual (row index 999 in the original pipeline), map selected bits to labels from the atlas label file, and save an aggregated CSV of selected labels across runs.
3. Load the aggregated selection table with `load_selection_table()`.
4. Flatten and count ROI selections across runs using `flatten_and_count()` to produce counts per ROI.
5. Run `binomial_test_and_fdr()` to compute p-values (one-sided binomial test), apply FDR correction, and compute Cohen's h effect sizes.
6. Print results to console and (optionally) save to CSV.

---

## 5. Statistical formulas (reference)

- Binomial one-sided p-value (observing at least k successes):

$$
P(X \ge k) = \sum_{i=k}^{n} \binom{n}{i} p_0^{i} (1-p_0)^{n-i}.
$$

- Cohen's h (effect size for proportions):

$$
h = 2\left(\arcsin\sqrt{p_1} - \arcsin\sqrt{p_2}\right),
$$

where $p_1$ is observed proportion (count / `n_trials`) and $p_2` is the expected proportion.

- Benjamini–Hochberg FDR is applied to control the false discovery rate across ROI tests.

---

## 6. Running the script

Run directly from the `Analysis` folder or from project root:

```bash
python Analysis/03_selected_roi_count.py
```

If you run on a headless server, ensure Matplotlib backend is configured (script does not plot by default).

---

## 7. Output

- Console: prints progress messages and the resulting DataFrame `results_df` with columns: `Region`, `Count`, `p-value`, `FDR-corrected p`, `Significant`, `Cohen's h`.
- CSV (optional): save `results_df` to `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv` by uncommenting the `to_csv` line in the script.

---

## 8. Notes and best practices

- Ensure `n_individuals` matches the number of GA result files you intend to process.
- Confirm the final-generation row index (999) matches how your GA outputs store the final individual; change the index if your GA saves the final individual at a different row.
- The binomial test assumes independent GA runs; take care when interpreting results if runs are correlated.
- Adjust `expected_p` if you use a different selection budget (not 15 ROIs) or a different ROI total.

---

