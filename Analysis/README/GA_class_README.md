# Usage Guide: `GA_class.py` 

This module provides utilities used by the GA pipeline: Ising-model parameter estimation (CPU/GPU), model-fit evaluation, local minima (basin) analysis, per-subject beta estimation, and helpers to load binarized brain data.

This README documents every function in the module and adds mathematical derivations and formulas used by the implementation.

---

## 1. Overview and data assumptions

- `task_data_train` is a list of binarized brain-activity arrays (each element is one subject). Each subject array contains binary values (0/1) for ROIs × time points.
- An ROI selection `individual` is a length-`N` vector of 0/1 values indicating which ROIs are selected.
- GPU mode uses PyTorch and requires CUDA-capable hardware when `use_gpu=True`.
- Many functions enumerate the full state-space (2^n). These are feasible only for small n (recommend n <= 16).

---

## 2. Mathematical background

Notation:
- Let s ∈ {−1,+1}^n denote a binary spin vector (Ising state). In code the raw data are 0/1; conversion is done via $s = 2x - 1$.
- h ∈ R^n are local fields; W ∈ R^{n×n} is a symmetric interaction matrix with zero diagonal.

Energy (Ising Hamiltonian)

$$
E(s) = -\frac{1}{2} \sum_{i,j} W_{ij} s_i s_j - \sum_i h_i s_i
$$

Probability of a state (Boltzmann/Gibbs)

$$
P(s) = \frac{e^{-E(s)}}{Z}, \quad Z = \sum_{s} e^{-E(s)}
$$

Empirical moments:
- Empirical mean per spin: $m_i^{\text{emp}} = \frac{1}{k} \sum_{t=1}^k s_i(t)$
- Empirical correlation: $C_{ij}^{\text{emp}} = \frac{1}{k} \sum_{t=1}^k s_i(t)s_j(t)$, with diagonal set to 0 for coupling estimation.

Moment-matching parameter estimation (used in `fit_approx_new` / `fit_approx_GPU`):
- Iterative updates aim to satisfy model moments $m^{\text{model}}$ and $C^{\text{model}}$ to match empirical moments. A common fixed-point-style update is:

$$
h \leftarrow h + \alpha (m^{\text{emp}} - m^{\text{model}})\\
W \leftarrow W + \alpha (C^{\text{emp}} - C^{\text{model}})
$$

In code, $m^{\text{model}}$ is computed as $\tanh(WX + h)$ averaged across samples and $C^{\text{model}}$ uses cross-terms between $X$ and $\tanh(\cdot)$.

Beta (per-subject scaling) estimation (used in `fit_approx_personal_new`):
- Given archetype parameters $(h^*, W^*)$, the model for subject s uses scaled parameters $\beta h^*, \beta W^*$.
- The algorithm minimizes difference between empirical energy and model-predicted energy, updating $\beta$ by gradient steps. Conceptually,

$$
H_{p}(\beta) = -\frac{1}{2} \sum_{i,j} W^*_{ij} \langle s_i s_j \rangle_{\text{model},\beta} - \sum_i h^*_i \langle s_i \rangle_{\text{model},\beta}
$$

and $\beta$ is updated to reduce $|\langle E \rangle_{\text{emp}} - H_{p}(\beta)|$.

Model-fit / accuracy measures (used in `calc_accuracy`):

- Let $p_n$ be the empirical distribution over states, $p_1$ the independent model (product of marginals), and $p_2$ the Ising model distribution.
- Entropy-based measure:

$$
H(p) = -\sum_s p(s) \log_2 p(s)
$$

$$
\text{acc}_1 = \frac{H(p_1) - H(p_2)}{H(p_1) - H(p_n)}
$$

- KL-based measure: define

$$
D(p_n \| p_1) = \sum_s p_n(s) \log_2 \frac{p_n(s)}{p_1(s)}, \quad D(p_n \| p_2) = \sum_s p_n(s) \log_2 \frac{p_n(s)}{p_2(s)}
$$

Then

$$
\text{acc}_2 = \frac{D(p_n\|p_1) - D(p_n\|p_2)}{D(p_n\|p_1)}
$$

Both measures lie near 0 when the Ising model provides no benefit over independence, and approach 1 as the Ising model better explains empirical statistics.

Basins and local minima

- Enumerate all states $s$. For each state compute its energy $E(s)$. For each state, consider one-bit-flip neighbors and find the neighbor with the smallest energy; that defines a directed map from each state to a neighbor. The fixed points (states that map to themselves) are local minima (basins). The basin graph groups states by which local minimum they flow to.

---

## 3. Function reference (complete)

All functions below are present in `GA_class.py`. Each description includes arguments, returns, algorithm summary, and complexity notes.

### func_ELA(individual, task_data_train, behavioral_df=None, use_gpu=False)
- Purpose: GA evaluation function. Using selected ROIs, fit an Ising model, compute per-subject beta estimates, return variance of betas, average accuracy, and number of local minima.
- Args:
  - `individual`: array-like 0/1 selection vector.
  - `task_data_train`: list of binary arrays (subjects). Each array is indexed by ROI (rows) and time (columns) after selection.
  - `behavioral_df`: unused in current implementation.
  - `use_gpu`: bool, attempt GPU fitting if True.
- Returns: `(var, acc, num)` where `var` is variance of subject betas, `acc` is mean of two accuracy scores, `num` is number of basins (local minima).
- Algorithm summary:
  1. Create boolean mask from `individual`; apply to each subject's data producing `filter_list`.
  2. Concatenate across subjects to form a dataset for archetype fitting.
  3. If `use_gpu`, call `fit_approx_GPU` to estimate `h` and `W` (PyTorch tensors); else call `fit_approx_new` (NumPy).
  4. Compute basin graph via `calc_basin_graph(h, W, task_data)` to get `num`.
  5. Compute model-fit accuracies via `calc_accuracy(h, W, task_data)`.
  6. For each subject, estimate per-subject beta with `fit_approx_personal_new` and compute variance over subjects.
- Complexity: archetype fit scales with O(n^2 k) per iteration where n is selected ROI count and k is sample size; basin and full-state computations scale as O(2^n) and are feasible only for small n.

### fit_approx_GPU(X_in: pd.DataFrame, max_iter: int = 10**3, alpha: float = 0.9)
- Purpose: GPU-accelerated iterative estimation of h and W using PyTorch.
- Args: `X_in` (DataFrame or tensor-like), `max_iter`, `alpha`.
- Returns: `(h, W, h_cpu, W_cpu)` where `h` and `W` are torch tensors on device, and `h_cpu`, `W_cpu` are NumPy arrays.
- Algorithm summary: Convert X to {-1,+1}, compute empirical mean and correlation, iterate update rules until convergence or max_iter. Uses matrix operations for efficiency.
- Notes: Device must be CUDA; the function returns both GPU tensors and CPU copies for compatibility.

### fit_approx_personal_new(X_in, h_archetype, W_archetype, max_iter=10**3, alpha=0.9)
- Purpose: Estimate subject-level scalar `\beta` that scales archetype parameters to best match subject empirical statistics.
- Args: subject data `X_in` (0/1), archetype `h_archetype`, `W_archetype` (NumPy arrays or Series/DataFrame), `max_iter`, `alpha`.
- Returns: scalar `beta`.
- Algorithm summary: Convert X to {-1,+1}, compute empirical energy, iterate gradient-like updates for beta so model energy $H_p(\beta)$ approximates empirical energy.
- Math sketch: update rule is a scalar gradient descent on difference between empirical energy mean and model-predicted energy.

### calc_state_no(X)
- Purpose: Convert binary rows to integer state indices (binary string -> decimal).
- Arg: `X` (DataFrame) where each row is a binary vector.
- Return: pd.Series of integers.
- Note: Implementation stringify rows and parse base-2.

### gen_all_state(X_in)
- Purpose: Generate full state matrix of shape (n × 2^n) where n = number of rows in `X_in`.
- Arg: `X_in` (DataFrame used to infer n)
- Return: DataFrame of 0/1 states.
- Complexity: O(2^n) memory/time.

### calc_prob(h, W, X)
- Purpose: Compute Boltzmann probabilities for each state in `X`.
- Args: `h`, `W` and `X` (DataFrame of states)
- Return: normalized probability vector.
- Formula: $p(s) \propto e^{-E(s)}$ with energy as above.

### calc_energy(h, W, X_in)
- Purpose: Compute energy value(s) for state(s) in `X_in` (0/1 or DataFrame/Series).
- Return: scalar or Series of energies.
- Formula: energy computed after mapping X_in to s ∈ {−1,+1}.

### fit_approx_new(X_in: pd.DataFrame, max_iter=10**3, alpha=0.9)
- Purpose: CPU implementation of iterative moment-matching parameter estimation.
- Returns: `(h, W)` as NumPy arrays (or h Series and W DataFrame in code).
- Update rules: see Section 2 (moment matching). Implementation computes $Y = \tanh(WX + h)$ per iteration, updates h and W by empirical minus model moments.

### calc_accuracy(h, W, X)
- Purpose: Compute two accuracy metrics comparing independent model, empirical distribution, and Ising model.
- Args: `h`, `W`, `X` (DataFrame with rows=ROIs)
- Returns: `(acc1, acc2)` as floats.
- Math: See Section 2 for entropy-based and KL-based formulas. Implementation computes empirical frequency distribution, independent-model probabilities, and Ising-model probabilities over enumerated states.

### calc_basin_graph(h, W, X)
- Purpose: Build a directed graph mapping each state to the adjacent state with the lowest energy; identify local minima as states mapping to themselves and assign basin labels.
- Args: `h`, `W`, `X` (DataFrame used to infer n)
- Returns: `(graph, num_local_minima)` where `graph` is a DataFrame with `source`, `target`, `energy`, `state_no`, and `num_local_minima` is integer count.
- Algorithm: Enumerates all states (`gen_all_state`), computes adjacency (`calc_adjacent`), computes energies, finds min-energy neighbor per state, constructs DiGraph and computes weakly connected components to assign basin indices.

### calc_adjacent(X)
- Purpose: For each state, produce integer indices of itself and all single-bit flips (neighbors).
- Args: `X` (DataFrame to infer n)
- Returns: DataFrame of state indices used in basin mapping.

### plot_local_min(data, graph, group, iter)
- Purpose: Visualize local minimum states as a heatmap. Uses `graph` rows where `source == target`.
- Args: `data`, `graph`, `group`, `iter` (group/iter used for titles or saving)
- Output: shows a heatmap figure (no return value).

### plot_local_min_s1(data, graph)
- Purpose: Return matrix of local minima states and their decimal indices.
- Returns: `(df, X_10)` where `df` is binary matrix (ROI × state_no) and `X_10` is list/array of decimal indices.

### load_brain_data_0(pkl_path, group_split=False)
- Purpose: Load `.pkl` files from a directory, filter out entries of shape (0,0), and optionally split by `dx_group` using matching `participants_*.tsv` files.
- Args: `pkl_path` directory; `group_split` bool.
- Returns:
  - If `group_split==False`: `(task_data_all, id_df)`
  - If `group_split==True` and group info found: `(group1_data, group2_data, id_df)`
- Behavior: For each `.pkl` file, looks for corresponding `participants_{name}.tsv`. Filters paired data to remove invalid shapes, flattens nested lists, prints brief debug counts.

### load_brain_data(pkl_path, group_split=False)
- Purpose: Similar to `load_brain_data_0` but with slightly different filename rules for participants files and fallback behavior when TSV missing.
- Returns: same shapes as above.

### main()
- Purpose: Example / utility workflow that loads training data and recomputes `func_ELA` across stored best individuals, caching repeated evaluations.
- Behavior: reads `ELAGAopt_result/GA_result/best_individual/best_ind_{k+1}.csv` files, for each row runs `func_ELA` with `use_gpu=True` (if available), caches results in-memory (`memo_result`, `memo_acc`) and writes per-run CSVs for var and acc.
- Output files: per-run CSVs under `ELAGAopt_result/GA_result/var/` and `.../acc/`.

---

## 4. Complexity and practical recommendations

- Archetype fit (`fit_approx_new`/`fit_approx_GPU`) scales roughly O(n^2 k) per iteration; keep `n` (selected ROI count) modest when possible.
- Full-state enumeration functions (`gen_all_state`, `calc_basin_graph`, `calc_prob`, `calc_accuracy`) scale exponentially O(2^n). Use for small n (<= 16) only or on reduced subsets extracted by the GA.
- Use GPU mode for large data or many subjects to accelerate matrix operations (PyTorch). Ensure CUDA drivers and PyTorch with CUDA are installed.

---

## 5. Usage examples

Basic ELA evaluation with loaded data:

```python
from GA_class import func_ELA, load_brain_data_0

task_data_train, _ = load_brain_data_0("Data//test_data_4//Run01_500")
individual = [0]*264
# select first 15 ROIs for example
for i in range(15):
    individual[i] = 1
var, acc, num = func_ELA(individual, task_data_train, use_gpu=False)
print("var, acc, num:", var, acc, num)
```

Run the module's utility main (example):

```bash
python GA_class.py
```

---

## 6. References and further reading

- Moment-matching / pseudo-likelihood / mean-field approximations for Ising models (review articles on statistical inference for binary network models).

---

If you want, I can:
- produce a separate LaTeX/PDF with the derivations, or
- add inline numeric examples (small n) and automated unit tests demonstrating each function on toy data.
