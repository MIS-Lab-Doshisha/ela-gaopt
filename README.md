# ela-gaopt
ELA/GAopt: Energy Landscape Analysis with Automated Region-of-Interest Selection via Genetic Algorithms

This repository contains the code for our paper: **Energy Landscape Analysis with Automated Region-of-Interest Selection via Genetic Algorithms** 

**ELA/GAopt** is a framework for data-driven ROI (Region Of Interest) optimization in Energy LAndscape Analysis(ELA).

A genetic algorithm-based optimisation framework for data-driven ROI (region of interest) selection in ELA.This repository contains code for selecting ROIs from brain activity (fMRI) data and analysing their properties.

This code has been tested with Python **3.13.2.**

## Table of Contents

- [ela-gaopt](#ela-gaopt)
  - [Table of Contents](#table-of-contents)
  - [1.  Install Dependencies](#1--install-dependencies)
  - [2. Prepare the Dataset for ELA/GAopt](#2-prepare-the-dataset-for-elagaopt)
    - [2.1 Brain activity data](#21-brain-activity-data)
    - [2.2 Brain atlas labels](#22-brain-atlas-labels)
    - [2.3. Output directory structure](#23-output-directory-structure)
  - [3. How to use](#3-how-to-use)
    - [3.1 Preprocessing of brain activity data.](#31-preprocessing-of-brain-activity-data)
      - [Input data settings:](#input-data-settings)
        - [Output:](#output)
    - [3.2 ROI selection optimization using ELA/GAopt.](#32-roi-selection-optimization-using-elagaopt)
      - [Definition of key parameters](#definition-of-key-parameters)
        - [Input data settings:](#input-data-settings-1)
        - [Output:](#output-1)
    - [3.3 Evaluation and visualisation of ROI optimization results](#33-evaluation-and-visualisation-of-roi-optimization-results)
    - [3.4 Comparison with random ROI selection.](#34-comparison-with-random-roi-selection)
    - [3.5 Analysis of local minimum states](#35-analysis-of-local-minimum-states)
    - [3.6. Intergroup comparison (ASD vs CTL)](#36-intergroup-comparison-asd-vs-ctl)
---



## 1.  Install Dependencies

Install the required Python packages using the provided : `requirements.txt` 

```
pip install -r requirements.txt
```
## 2. Prepare the Dataset for ELA/GAopt

### 2.1 Brain activity data

* Prepare brain activity time series data and store in the `Data/` directory.

* This project uses `.nii.gz` files to store brain activity data. Example data can be found in the `Data/preprocessed/` directory.
  
**Directory structure**:
```
Data/
├── preprocessed/
│   ├── derivatives/
│   │   └── sub-XXXX/
│   │       └── func/
│   │           └── sub-XXXX_task-rest_space-XXXX_res-2_desc-preproc_bold.nii.gz
│   └── particpiants.tsv
├── test_data/
│   ├── discovery/
│   │   └── task_data_train.pkl
│   └── test/
│        └── test_data.pkl
└── atlas_data/
```

### 2.2 Brain atlas labels
* Place the ROI label files for the Atlas used (e.g. Power264) in the `Data/atlas_data/` directory.

* `power264NodeNames.txt` and `dosenbach160NodeNames.txt` are used in this project.

### 2.3. Output directory structure

The script stores the analysis results under the `ELAGAopt_result/` directory. 


## 3. How to use

Each script corresponds to a specific analysis step. It is recommended that they be run in the following order
Set variables, paths, etc. in the scripts to suit your environment.

### 3.1 Preprocessing of brain activity data.

The `00_brain_data.py` script reads a `.nii.gz` file from the given path, extracts the ROI time series using `nilearn`, binarises it and saves it as a `.pkl` file.

#### Input data settings:

* fMRI BOLD data (in `.nii.gz` format, specified by `subjects_path`).
* confound file (in `.tsv` format)
* `.tsv` file containing information on each subject (in `participants.tsv` format, specified by `behavioral_path`)

Once the input data are correctly defined, run the script.
```
python Analysis/00_brain_data.py
```

##### Output:
* Binarized brain activity data (in `.pkl` format, specified by `pkl_path`).


### 3.2 ROI selection optimization using ELA/GAopt.
`01_main_ELAGAopt.py` searches for the best ROI set by GA.

`GA_class.py` is a core class that provides parameter estimation, model fit calculations, local minimum state analysis and GA objective functions (`func_ELA`) for pMEM. GPU use is also supported.

#### Definition of key parameters

| Parameter              | Description                             |
|--------------------|------------------------------------------|
| `INDIVIDUAL_LENGTH` | Individual length (number of ROIs)       |
| `MAX_ONES`          | Number of ROIs to select                 |
| `POPULATION_SIZE`   | Population size                          |
| `CROSSOVER_PROB`    | Crossover probability                    |
| `MUTATION_PROB`     | Mutation probability                     |
| `MAX_GENERATIONS`   | Maximum number of generations            |
| `FITNESS_THRESHOLD` | Optimization termination condition       |

##### Input data settings:
* Binarized brain activity data (created in `00_brain_data.py`.Specified by `pkl_path`)

Once the input data are correctly defined, run the script.
```
python Analysis/01_main_ELAGAopt.py
```

##### Output:
All output destinations are specified by `output_path`.
| Output File               | Description                             |
|--------------------|------------------------------------------|
| `best_ind_{seed}.csv`     | Best individuals of each generation       |
| `best_fitness_{seed}.csv` | Best objective function value for each generation                 |
| `population_{seed}.pkl`   | List of individuals of each generation.                         |
| `fitness_{seed}.pkl`      | List of objective function values for each generation.                  |


### 3.3 Evaluation and visualisation of ROI optimization results
Once the ROI selection by **ELA/GAopt** has been completed, the selection should be evaluated.Scripts for this evaluation can be found in the `Analysis/` directory.

* `02_GA_plot.py`: Plot the generation-by-generation evolution of the objective function values over multiple GA runs.
* `03_selected_roi_count.py`: The frequency of ROIs selected by ELA/GAopt is tabulated and significantly selected ROIs are identified using binomial tests and FDR correction.
* `04_selected_roi_search.py`: Search for the best ROI individuals, consisting only of ROIs that are still considered significant after FDR correction.
* `05_roi_visualization.py`: The number of times a significantly selected ROI has been selected is visualised in a bar chart.
* `06_ELAGAopt_result_check.py`: Detailed evaluation of pMEM fitting accuracy, beta variance, number of local stable states, etc. for the best ROI individuals selected by ELA/GAopt.
* `roi_selection_analysis.py` : Functions related to ROI selection analysis (ROI tabulation, binomial test, FDR correction, significant individual search, plots).


### 3.4 Comparison with random ROI selection.

* `10_permutation_random_data_create.py`: Calculate pMEM fitting accuracy and beta variance in randomly selected ROI individuals to generate a baseline dataset for permutation testing.
* `11_random_roi_selection.py`: The local min Hamming distance between the discovery and the test data is also calculated.
*  `12_permutation_test.py`: Objective function values of ROI individuals selected by **ELA/GAopt** are compared with objective function values of randomly selected ROI individuals and are subjected to Permutation test, t-test, Mann-Whitney U test, Cohen's d calculation and visualisation.


### 3.5 Analysis of local minimum states
* `21_local_min_freq_calc.py`: Calculate the frequency of occurrence of local minimum states in the brain activity data of all subjects for each ROI set selected in ELA/GAopt
* `22_local_min_freq_mannwhutneyu.py`: Mann-Whitney U test between groups (e.g. ASD vs CTL) for frequency of occurrence of local stable states, effect size r calculation, FDR correction

### 3.6. Intergroup comparison (ASD vs CTL)
* `31_ASD_CTL_compare.py`: Comparison of pMEM metrics (beta variance, fitting accuracy, number of local minimum states) between ASD and CTL groups using ROI individuals selected by ELA/GAopt.
* `32_roi_mannwhitneyu_test.py`: Mann-Whitney U test and effect size r calculation for indicators such as the number of local stable states in the ASD and CTL groups.

For more details, refer to the scripts.



