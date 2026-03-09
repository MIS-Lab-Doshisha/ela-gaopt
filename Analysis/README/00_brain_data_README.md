# Usage Guide: `00_brain_data.py`

This script is used to extract fMRI time-series data from preprocessed ABIDE (Autism Brain Imaging Data Exchange) datasets and convert them into binarized formats for use in Energy Landscape Analysis (ELA) or Genetic Algorithm (GA) optimizations.

## Overview
The script identifies specific Brain Regions of Interest (ROIs) based on the Power 2011 Atlas (264 nodes), extracts the neural signals using spherical masking, cleans the signals through confound regression and filtering, and finally binarizes the data relative to the mean signal of each ROI.

---

## 1. Input Data Requirements

### A. Preprocessed fMRI Data (ABIDE)
The script expects preprocessed BOLD NIfTI files in fMRIPrep-style directory structure:
- **Location:** Defined by `subjects_path` (e.g., `Data//preprocessed//derivatives//`)
- **File Pattern:** `sub-{subject}/func/sub-{subject}_task-rest_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz` (session-free), or with session: `sub-{subject}_task-rest_{session}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz`

### B. Behavioral Data
- **File:** `participants.tsv` (located in `behavioral_path`)
- **Format:** Tab-separated file containing at minimum:
  - `participant_id`: Subject identifier (e.g., `sub-40001`)
  - `site_id`: Site identifier for the ABIDE dataset

### C. Brain Atlas
- **Atlas:** Power Atlas (2011)
- **ROIs:** 264 spherical coordinates.
- **Source:** Automatically fetched using `nilearn.datasets.fetch_coords_power_2011()`.

---

## 2. Output Data

### A. Pickle File (.pkl)
The final output is a serialized Python object containing the processed data for all subjects.
- **Path:** `Data//test_data_1//test//` (configurable via `pkl_path`)
- **Default filename:** `test_data.pkl` (currently commented out in script)
- **Structure:** A `list` of `numpy.ndarray` objects.
- **Array Shape:** `(Time points, 264)`
- **Values:** Binary (`0` or `1`).

### B. Visualization Output
- **Time Series Plots:** PNG files saved as `Data/GIFT_data/TimeSeries00_sub-{subject}.png` for visual inspection of extracted signals.

---

## 3. Configuration (Global Variables)

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `TR` | float | `2.0` | Repetition Time (seconds). |
| `radius` | int | `4` | Radius of the spherical ROI (mm). |
| `raw_site_name` | list | `["ABIDE2-USM_1"]` | List of ABIDE site names to process. |
| `session_list` | list | `[""]` | Session identifiers (empty string for single session). |
| `subjects_path` | str | `"Data//preprocessed//derivatives//"` | Path to the root directory of preprocessed ABIDE data. |
| `behavioral_path` | str | `"Data//preprocessed//"` | Path to the directory containing behavioral data. |
| `pkl_path` | str | `"Data//test_data_1//test//"` | Directory where the output `.pkl` will be saved. |

---

## 4. Function Definitions

### `time_series(...)`
Extracts and cleans the BOLD signal from the NIfTI images.
- **Arguments:**
    - `subject_list` (list): IDs of subjects to process.
    - `session_list` (list): Session identifiers (e.g., empty string `""` for single session).
    - `subjects_location` (str): Base path to the preprocessed data.
    - `all_mni_coords` (list): List of (x, y, z) coordinates for ROIs.
    - `radius` (int): Masker sphere radius.
    - `TimeSeries_list` (list): Accumulator list for the results.
- **Returns:** Updated `TimeSeries_list` containing 2D arrays (shape: `Time x ROI`).
- **Processing Details:**
    - **Confounds:** High-pass filter, motion (full parameters), WM/CSF signals, and scrubbing (FD > 0.5mm).
    - **Filtering:** Band-pass filter between 0.01 Hz and 0.1 Hz.
    - **Smoothing:** 6mm FWHM kernel.
    - **Detrending:** Enabled.

### `binarize(...)`
Converts continuous signals into binary states (0/1) based on ROI-specific mean thresholds.
- **Arguments:**
    - `TimeSeries_list` (list): List of extracted signal arrays (Time x ROI).
    - `binarize_list` (list): Accumulator list for the binary data.
- **Returns:** Updated `binarize_list`.
- **Logic:** For each ROI (row), time points are set to `1` if the signal is greater than the mean of that specific ROI's time-series, and `0` otherwise.

### `main()`
The entry point of the script.
- **Logic:**
    1. Iterates through specified sites (`raw_site_name`).
    2. Loads participant data from the TSV file.
    3. Processes each subject sequentially.
    4. Calls `time_series` to extract data.
    5. Generates visualization plots.
    6. Calls `binarize` to convert data.
    7. Reshapes data and appends to output list.
    8. Saves final data to a pickle file (pickle dump currently commented out).

---

## 5. Execution Workflow
1. **Data Setup:** Reads Power 2011 atlas coordinates.
2. **Behavioral Loading:** Reads participant and site information from TSV file.
3. **Per-Subject Processing:**
   - Constructs the path to the BOLD image based on subject ID and session.
   - Loads the BOLD image and corresponding confounds.
   - Applies `NiftiSpheresMasker` for signal cleaning and extraction.
   - Generates a time series visualization plot.
4. **Binarization:** Processes the extracted signals ROI by ROI using mean-based thresholding.
5. **Data Reshaping:** Concatenates binarized signals across ROIs.
6. **Serialization:** Dumps the final list of arrays into a pickle file for subsequent ELA/GA analysis (currently disabled).

---

## 6. Notes

- **Session Handling:** The script supports both single-session and multi-session processing. Use empty string `""` for datasets without session identifiers, or specify session names (e.g., `["ses-01", "ses-02"]`) for multi-session datasets.
- **Site Flexibility:** Multiple ABIDE sites can be processed by adding them to the `raw_site_name` list.
- **Caching:** nilearn's `memory` mechanism is enabled for caching intermediate results, which speeds up repeated runs.
- **Pickle Dump:** The pickle file serialization is currently commented out in the `main()` function. Uncomment the lines at the end of the script to enable saving.
