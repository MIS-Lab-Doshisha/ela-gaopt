# Usage Guide: `00_brain_data_HCP.py`

This script is used to extract fMRI time-series data from preprocessed HCP (Human Connectome Project) datasets and convert them into binarized formats for use in Energy Landscape Analysis (ELA) or Genetic Algorithm (GA) optimizations.

## Overview
The script identifies specific Brain Regions of Interest (ROIs) based on the Power 2011 Atlas (264 nodes), extracts the neural signals using spherical masking, cleans the signals through confound regression and filtering, and finally binarizes the data relative to the mean signal of each ROI.

---

## 1. Input Data Requirements

### A. Preprocessed fMRI Data (HCP)
The script expects preprocessed BOLD NIfTI files. It follows the standard fMRIPrep-style directory structure:
- **Location:** Defined by `subjects_path` (e.g., `/media//HCP-YA/data/HCP_OUTPUT/`)
- **File Pattern:** `sub-{subject}/func/sub-{subject}_task-REST_acq-{session}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz`

### B. Subject List
- **File:** `Data/group_2_subjects.xlsx`
- **Format:** An Excel file containing a `participants` column with subject IDs (e.g., 100206).

### C. Brain Atlas
- **Atlas:** Power Atlas (2011)
- **ROIs:** 264 spherical coordinates.
- **Source:** Automatically fetched using `nilearn.datasets.fetch_coords_power_2011()`.

---

## 2. Output Data

### A. Pickle File (.pkl)
The final output is a serialized Python object containing the processed data for all subjects.
- **Path:** `Data/test_data_4/test_data_run01_500_5.pkl`
- **Structure:** A `list` of `numpy.ndarray` objects.
- **Array Shape:** `(Time points, 264)`
- **Values:** Binary (`0` or `1`).

---

## 3. Configuration (Global Variables)

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `TR` | float | `0.72` | Repetition Time (seconds). |
| `radius` | int | `4` | Radius of the spherical ROI (mm). |
| `session_list` | list | `["LR_run-01"]` | The specific fMRI run/session to process. |
| `subjects_path`| str | (Absolute path) | Path to the root directory of preprocessed HCP data. |
| `pkl_path` | str | `"Data/test_data_4/"`| Directory where the output `.pkl` will be saved. |

---

## 4. Function Definitions

### `time_series(...)`
Extracts and cleans the BOLD signal from the NIfTI images.
- **Arguments:**
    - `subject_list` (list): IDs of subjects to process.
    - `session_list` (list): Session identifiers (e.g., "LR_run-01").
    - `subjects_location` (str): Base path to the data.
    - `all_mni_coords` (list): List of (x, y, z) coordinates for ROIs.
    - `radius` (int): Masker sphere radius.
    - `TimeSeries_list` (list): Accumulator list for the results.
- **Returns:** Updated `TimeSeries_list` containing 2D arrays (shape: `Time x ROI`).
- **Processing Details:**
    - **Confounds:** High-pass, motion (24 parameters), WM/CSF signals, and scrubbing (FD > 0.5mm).
    - **Filtering:** Band-pass filter between 0.01Hz and 0.1Hz.
    - **Smoothing:** 6mm FWHM kernel.

### `binarize(...)`
Converts continuous signals into binary states (0/1).
- **Arguments:**
    - `TimeSeries_list` (list): List of extracted signal arrays (Time x ROI).
    - `binarize_list` (list): Accumulator list for the binary data.
- **Returns:** Updated `binarize_list`.
- **Logic:** For each ROI, time points are set to `1` if the signal is greater than the mean of that specific ROI's time-series, and `0` otherwise.

### `main()`
The entry point of the script.
- **Logic:**
    1. Loads subject IDs from the Excel file.
    2. Iterates through subjects.
    3. Calls `time_series` to extract data.
    4. Calls `binarize` to convert data.
    5. Formats the data into the final shape and saves it to a `.pkl` file.

---

## 5. Execution Workflow
1. **Coordinate Setup:** Fetches Power 2011 coordinates.
2. **Subject Loading:** Reads subject list from Excel.
3. **Signal Extraction (Per Subject):**
   - Loads BOLD image and corresponding confounds.
   - Applies `NiftiSpheresMasker` for signal cleaning and extraction.
4. **Binarization:** Processes the extracted signals ROI by ROI.
5. **Serialization:** Dumps the final list of arrays into a pickle file for subsequent ELA/GA analysis.
