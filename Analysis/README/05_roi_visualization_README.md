**05_roi_visualization: README**

- **Purpose:** Visualize ROI selection results produced by the GA analysis. This README covers two small scripts present in this repository: `05_roi_visualization_all.py` (plots selection counts for every ROI) and `05_roi_visualization_significant.py` (plots only FDR-significant ROIs and network summaries using `ROISelectionAnalyzer`).
- **Location:** Analysis/
- **Tested with:** Python 3.13.2

**Overview:**
- `05_roi_visualization_all.py`: Loads an FDR-corrected selection CSV (or aggregated selection-count CSV) and draws a bar plot of selection counts for all ROIs. It saves PNG and SVG outputs.
- `05_roi_visualization_significant.py`: Uses `ROISelectionAnalyzer` from `roi_selection_analysis.py` to produce more structured visualizations (per-ROI and per-network counts) for the FDR-corrected ROI list.

**Inputs:**
- `atlas_label_path` (string): Text file containing ROI labels for the atlas used (e.g., `Data/atlas_data/power264NodeNames.txt`).
- `fdr_table_path` (string): CSV file produced by `03_selected_roi_count.py` (e.g., `ELAGAopt_result/Analysis_result/selected_ROI_count/selected_test_data_fdr.csv`). Expected columns: `Region`, `Count` (for the simple plotting script). For `ROISelectionAnalyzer` usage the CSV is the same FDR result file.

**Outputs:**
- Image files saved to the specified `output_path` prefix. Examples produced by the simple script:
  - `ELAGAopt_result/Analysis_result/ROI_visualization/roi_selection_count_all.png`
  - `ELAGAopt_result/Analysis_result/ROI_visualization/roi_selection_count_all.svg`
- `05_roi_visualization_significant.py` delegates plotting to `ROISelectionAnalyzer.plot_roi_and_network_counts`, which will save files with the provided `output_prefix`.

**Configuration (script-level variables):**
- `atlas_label_path`: path to atlas labels file.
- `fdr_table_path`: path to FDR-corrected selection CSV.
- `output_path` / `output_prefix`: prefix / path used when saving plots.
- `expected_p` (used in `05_roi_visualization_significant.py` when constructing `ROISelectionAnalyzer`): expected selection probability under the null (default in example: 15/264). Tune this to match your GA selection probability assumption.

**Behavior / Workflow:**
1. Read the FDR-corrected CSV (or aggregated selection table).
2. For `05_roi_visualization_all.py`: draw a single large bar chart (`Region` vs `Count`), rotate x-ticks for readability, annotate each bar with its integer count, and save PNG+SVG.
3. For `05_roi_visualization_significant.py`: instantiate `ROISelectionAnalyzer(expected_p=...)`, then call `plot_roi_and_network_counts(...)`. That function reads label/ROI mapping, groups counts by network (if network assignment available in the labels), and saves per-ROI and per-network bar plots.

**Usage examples:**
- Run the simple all-ROI visualization script:

```bash
python Analysis/05_roi_visualization_all.py
```

- Run the significant-only visualization script:

```bash
python Analysis/05_roi_visualization_significant.py
```

Both scripts assume the working directory is the repository root and that the paths defined in the script are reachable.

**Plot appearance details:**
- `05_roi_visualization_all.py` uses a large figure  to accommodate many ROIs, sets bar color to blue and annotates counts above each bar. X labels are rotated 90 degrees.
- `05_roi_visualization_significant.py` relies on `ROISelectionAnalyzer` for plot styling; see `roi_selection_analysis_README_en.md` for details on network grouping and file-naming conventions.

**Notes & recommendations:**
- If the label file contains network assignments (e.g., Power atlas mapping of ROI→network), the analyzer can aggregate counts by network and save summarized plots.
- For many ROIs, SVG is preferred for scalable figures if you plan to edit them in vector graphic tools.
- If the FDR CSV contains additional columns (p-values, FDR q-values), consider embedding those into the `ROISelectionAnalyzer` visualizations or exporting annotated tables alongside images.

**Troubleshooting:**
- If plots are empty or counts are zero, verify `fdr_table_path` points to the correct CSV and inspect its header/column names (`Region`, `Count`).
- For label mismatch errors, confirm that `atlas_label_path` contains labels in the expected order and format matching the ROI indices used in your GA outputs.
