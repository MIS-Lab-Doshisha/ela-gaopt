# Usage Guide: `01_main_ELAGAopt.py`

This script performs Genetic Algorithm (GA) based optimization of ROI selection using DEAP library. It reads binarized brain fMRI data from HCP (Human Connectome Project) datasets, applies an evolutionary algorithm to select the best subset of ROIs (15 out of 264), and evaluates each candidate solution using an Ising model with Energy Landscape Analysis (ELA).

## Overview
The script implements a multi-objective GA optimization pipeline that:
1. Initializes a population of ROI selection candidates (binary individuals with exactly N ones)
2. Evaluates each individual using the ELA evaluation function
3. Applies genetic operators (crossover, mutation) with constraint repair to maintain the fixed number of selected ROIs
4. Tracks the best individual across generations
5. Saves results including best individuals, fitness values, and population history

---

## 1. Input Data Requirements

### A. Binarized Brain Data
The script expects preprocessed, binarized fMRI data in pickle format.
- **File:** Specified by `pkl_path` (e.g., `Data//test_data_4//Run01_500`)
- **Format:** A Python pickle file containing a list of `numpy.ndarray` objects.
- **Array Shape:** Each subject's data has shape `(Time points, 264)` where 264 is the number of ROIs from the Power Atlas.
- **Values:** Binary (`0` or `1`), already preprocessed by `00_brain_data_HCP.py`.
- **Function:** Data is loaded via `load_brain_data_0()` from `GA_class` module.

### B. GA Class Module
- **Module:** `GA_class.py`
- **Key Function:** `func_ELA()` - Evaluates an individual ROI selection using Ising model and returns fitness value.
- **Dependency:** Must be in the same directory as this script.

---

## 2. Output Data

### A. Best Individual per Run
- **Path:** `ELAGAopt_result//GA_result//best_individual//best_ind_500_{seed_id}.csv`
- **Format:** CSV file
- **Content:** The best ROI selection candidate found after all generations.
- **Shape:** One row per generation, representing the evolution of the best individual.

### B. Objective Function History
- **Path:** `ELAGAopt_result//GA_result//objective_function//best_fitness_500_{seed_id}.csv`
- **Format:** CSV file
- **Content:** Best fitness value for each generation.

### C. Fitness Distribution per Generation
- **Path:** `ELAGAopt_result//GA_result//fitness//fitness_500_{seed_id}.pkl`
- **Format:** Pickle file
- **Content:** A list of fitness lists, where each inner list contains all fitness values in that generation.
- **Structure:** `fit_list[generation_i] = [fitness_1, fitness_2, ... fitness_100]` (for POPULATION_SIZE=100)

### D. Population History
- **Path:** `ELAGAopt_result//GA_result//population//population_500_{seed_id}.pkl`
- **Format:** Pickle file
- **Content:** Complete population (all individuals) saved as a DataFrame for each generation.
- **Structure:** `pop_list[generation_i]` = DataFrame of 100 individuals (for POPULATION_SIZE=100)

---

## 3. Configuration (Global Variables)

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `INDIVIDUAL_LENGTH` | int | `264` | Number of ROIs in the Power Atlas (total genes per individual). |
| `MAX_ONES` | int | `13` | Number of ROIs to select (fixed number of 1s in each individual). |
| `POPULATION_SIZE` | int | `100` | Number of individuals in the population per generation. |
| `CROSSOVER_PROB` | float | `1.0` | Probability of crossover operation. |
| `MUTATION_PROB` | float | `1.0` | Probability of mutation operation. |
| `MAX_GENERATIONS` | int | `1000` | Maximum number of generations before stopping. |
| `FITNESS_THRESHOLD` | int | `10` | Fitness threshold for early stopping condition. |
| `pkl_path` | str | `"Data//test_data_4//Run01_500"` | Path to the binarized brain data pickle file. |
| `output_path` | str | `"ELAGAopt_result//GA_result"` | Root directory for saving output results. |

---

## 4. Function Definitions

### `init_individual()`
Initializes a single individual by creating a binary vector with exactly `MAX_ONES` ones and zeros, randomly shuffled.
- **Returns:** A `creator.Individual` object with `INDIVIDUAL_LENGTH` genes.
- **Logic:** Creates a list with `MAX_ONES` ones and `INDIVIDUAL_LENGTH - MAX_ONES` zeros, then shuffles it.

### `lamarckian_repair(individual, max_ones=MAX_ONES)`
Repairs an individual to ensure it has exactly `max_ones` ones (constraint satisfaction).
- **Arguments:**
    - `individual` (list): The individual to repair.
    - `max_ones` (int): The target number of ones.
- **Logic:**
    - If individual has too many ones, randomly flip excess ones to zeros.
    - If individual has too few ones, randomly flip zeros to ones.
- **Modifies:** The individual in-place.

### `constrained_mate(parent1, parent2)`
Performs two-point crossover and applies Lamarckian repair to both offspring.
- **Arguments:**
    - `parent1`, `parent2` (Individual): Parent individuals.
- **Returns:** Repaired parent1 and parent2.
- **Logic:** Calls `toolbox.mate()` then repairs each offspring to maintain exactly `MAX_ONES` ones.

### `constrained_mutate(individual)`
Performs bit-flip mutation and applies Lamarckian repair to the individual.
- **Arguments:**
    - `individual` (Individual): The individual to mutate.
- **Returns:** Repaired individual.
- **Logic:** Performs mutation with probability `1/INDIVIDUAL_LENGTH` per gene, then repairs to maintain exactly `MAX_ONES` ones.

### `evaluate_individual(individual)`
Evaluates an individual by computing the Ising model fitness using `func_ELA()`.
- **Arguments:**
    - `individual` (list): Binary ROI selection vector.
- **Returns:** Tuple `(fitness_value,)` - Sum of result and accuracy from `func_ELA()`.
- **Note:** GPU acceleration is enabled via `use_gpu=True`.

### `main(seed)`
The primary GA optimization loop.
- **Arguments:**
    - `seed` (int): Random seed for reproducibility.
- **Logic:**
    1. Initializes population and multiprocessing pool.
    2. Evaluates initial population.
    3. Iterates through generations until `MAX_GENERATIONS` or `FITNESS_THRESHOLD` is reached.
    4. Applies selection, crossover, mutation with constraint repair.
    5. Tracks best individual and fitness per generation.
    6. Saves results to CSV and pickle files.
- **Parallelization:** Uses multiprocessing with 29 cores by default.

---

## 5. Execution Workflow
1. **Data Loading:** Loads binarized brain data from pickle file via `load_brain_data_0()`.
2. **DEAP Setup:** Initializes toolbox with genetic operators and fitness function.
3. **Population Initialization:** Creates initial population of `POPULATION_SIZE` random individuals.
4. **Initial Evaluation:** Evaluates all individuals using `func_ELA()` with GPU acceleration.
5. **Main GA Loop:**
   - Selection: Tournament selection (tournament size = 3)
   - Crossover: Two-point crossover with probability `CROSSOVER_PROB`
   - Mutation: Bit-flip mutation with probability `MUTATION_PROB`
   - Constraint Repair: Lamarckian repair after each genetic operation
   - Evaluation: Evaluate invalid (modified) individuals only
   - Tracking: Update best individual and generation statistics
6. **Termination:** Stop when `MAX_GENERATIONS` is reached or fitness exceeds `FITNESS_THRESHOLD`.
7. **Results Saving:** Save best individual, fitness history, and population snapshots to output directory.

---

## 6. Multiprocessing Configuration

- **CPU Pool Size:** Defaults to 29 cores (set in `main(seed)`)
- **Purpose:** Parallel evaluation of individuals within each generation
- **Benefit:** Significant speedup for computationally expensive `func_ELA()` evaluations

---

## 7. Execution Instructions

### Single Run
```python
main(seed=11000)
```

### Multiple Runs (with different seeds)
The main block already provides a loop with incrementing seeds. Modify as needed:
```python
if __name__ == "__main__":
    seed = 11000
    for i in range(100):
        seed += 1000
        print("start:", seed)
        main(seed)
```

### Notes
- Each run will generate 4 output files per seed (best_ind, best_fitness, fitness, population).
- The seed ID in filenames is `seed//1000` (integer division), so seed `12000` produces files with `_12.csv`.
- Ensure output directories exist: `ELAGAopt_result/GA_result/best_individual/`, etc.
- GPU is required for efficient computation (controlled by `use_gpu=True` in `func_ELA()`).

---

## 8. Notes

- **Constraint Handling:** The Lamarckian repair mechanism ensures all individuals are valid solutions with exactly `MAX_ONES` ROIs selected at all times.
- **Fitness Evaluation:** The fitness function combines the Ising model result and accuracy from ELA, providing a multi-objective evaluation.
- **Population Preservation:** Only invalid individuals (those modified by genetic operators) are re-evaluated, reducing computational cost per generation.
- **Early Stopping:** Evolution terminates if any individual achieves a fitness value >= `FITNESS_THRESHOLD` before reaching `MAX_GENERATIONS`.
