# Usage Guide: `04_selected_roi_search.py` 

This script searches for GA individuals (columns) composed entirely of ROIs flagged as significant by FDR. It uses the aggregated selection table and the FDR-corrected ROI list produced by earlier analysis steps to identify individuals whose every selected ROI appears in the significant ROI set.

The README below follows the same chapter/section structure used by other Analysis READMEs (inputs → outputs → configuration → workflow → formulas → execution → notes).

---

## Overview

- Entry script: `04_selected_roi_search.py`
- Purpose: find indices of individuals (columns) in a selection table where all ROIs are FDR-significant.
- Typical inputs: selection summary CSV produced by `03_selected_roi_count.py` and an FDR-corrected ROI CSV from the same analysis.
- Typical use-case: post-hoc screening of GA final individuals to locate those composed only of significantly selected ROIs.

---

## 1. Input Data Requirements

### A. Selection summary table
- Path (default in script): `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv`
- Format: CSV produced by `03_selected_roi_count.py` where each column corresponds to one GA run (or individual) and entries list selected ROI labels for that run.
- Expected structure: header + columns of ROI labels; missing entries may be empty or NaN.

### B. FDR-corrected ROI list
- Path (default in script): `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv`
- Format: CSV containing at least `Region` and `Significant` columns (as produced by `ROISelectionAnalyzer.binomial_test_and_fdr`).
- The script uses the `Region` values where `Significant == True` to form the reference set.

---

## 2. Output Data

- Console output listing indices (integer positions) of individuals (columns) that are composed only of ROIs marked significant in the FDR CSV.
- No files are written by default; results are printed to stdout. You can redirect output to a file or modify the script to save results to CSV.

---

## 3. Configuration (values used in the script)

| Variable | Type | Default (in script) | Description |
| :--- | :--- | :--- | :--- |
| `select_table_path` | str | `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data.csv` | Path to selection summary table. |
| `fdr_table_path` | str | `ELAGAopt_result//Analysis_result//selected_ROI_count//selected_test_data_fdr.csv` | Path to FDR-corrected ROI CSV. |
| `ROISelectionAnalyzer` params | float,int | `expected_p=15/264`, `n_trials=66` (example) | Analyzer instance parameters; adjust depending on how FDR was computed. |

Adjust these paths and parameters in the script before running if your files differ.

---

## 4. Functionality and algorithm

### Primary operation performed by the script
1. Instantiate `ROISelectionAnalyzer` with `expected_p` and `n_trials` (these values are not strictly required for the search but follow the analyzer interface).
2. Call `find_all_significant_individuals(fdr_csv_path, select_csv_path)` which:
   - Loads the FDR CSV and extracts the set of ROI names with `Significant == True`.
   - Loads the selection table CSV and iterates over each column (individual).
   - For each individual, collects its listed ROI labels (dropping NaN) and checks whether every label is present in the significant ROI set.
   - If all labels are significant, records the column index.
3. Print the list of matching indices. If none are found, print a message indicating so.

### Complexity
- Time complexity: O(M * L) where M is number of individuals (columns) and L is average number of ROIs selected per individual (typically small, e.g., 15). File I/O and CSV parsing dominate for large M.
- Memory: minimal; the script loads two CSVs and iterates columns without duplicating large structures.

---

## 5. Statistical considerations (reference)

- This search is deterministic: it only checks set membership between the selected ROI labels for an individual and the set of FDR-significant ROI labels.
- Ensure that ROI label strings are normalized in both files (no extra whitespace, the same naming/casing scheme). The implementation strips whitespace when building the comparison set.

---

## 6. Execution instructions

Run from project root or `Analysis` folder:

```bash
python Analysis/04_selected_roi_search.py
```

Pre-run checklist:
- Confirm `select_table_path` exists and contains ROI labels in columns.
- Confirm `fdr_table_path` exists and contains `Region` and `Significant` columns.
- If using different file locations, edit the variables at the top of `04_selected_roi_search.py`.

---

## 7. Example output

- When matches are found, the script prints lines such as:

```
Indices of individuals (columns) composed only of significant ROIs:
5
12
```

- When no matches are found, the script prints:

```
No individuals composed only of significant ROIs were found.
```

---

## 8. Extending the script

- Save results: modify the script to write matching indices to a CSV or JSON file instead of printing.
- Relaxed matching: allow a threshold (e.g., at least 80% of ROIs significant) by changing the membership check to a proportion test.
- Label normalization: if labels differ across files, add a mapping table or normalization step (lowercasing, removing prefixes/suffixes) before comparison.

---