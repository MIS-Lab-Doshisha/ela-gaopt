"""
Isingモデル評価・局所安定状態解析クラス
--------------------------------------
このモジュールは、GAで選択されたROI個体に対してIsingモデルのパラメータ推定、適合度評価、局所安定状態（local minima）解析を行う関数群を提供します。

Ising model evaluation and local minima analysis class
-----------------------------------------------------
This module provides functions for parameter estimation, model fit evaluation, and local minima analysis of Ising models for ROI individuals selected by GA.
"""

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os

sns.set_context('talk', font_scale=0.8)

def func_ELA(individual, task_data_train, behavioral_df=None, use_gpu=False):
    """
    Evaluation function for GA

    Parameters
    ----------
    individual :  List of selected ROIs (e.g., (1,0,0,...,0,1), length=160)
    task_data_train :  List of binarized brain activity data (subjects × (ROIs × time points))
    behavioral_df :  Behavioral data 

    Returns
    -------
    var : Variance of individual parameters
    acc : Fitting accuracy to the Ising model
    num : Number of local minima.
    """

    selection_mask = np.array(individual, dtype=bool)
    filter_list = [data[selection_mask].astype('int32') for data in task_data_train]
    task_data = np.concatenate(filter_list, axis=1)
    task_data = pd.DataFrame(task_data)
    task_data.columns = range(task_data.shape[1])
    if use_gpu:
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        tensor_list = [torch.tensor(data.astype('float32'), device=device) for data in filter_list]
        task_data_tensor = torch.cat(
            [t.unsqueeze(1) if t.ndim == 1 else t for t in tensor_list],
            dim=1
        )
        
        _, _, h, W = fit_approx_GPU(task_data_tensor)
        _, num = calc_basin_graph(h, W, task_data)
        task_data = pd.DataFrame(np.concatenate(filter_list, axis=1))
        acc1, acc2 = calc_accuracy(h, W, task_data)
    else:
        h, W = fit_approx_new(task_data)
        _, num = calc_basin_graph(h, W, task_data)
        acc1, acc2 = calc_accuracy(h, W, task_data)
    acc = (acc1 + acc2) / 2

    beta_list = []
    for filtered in filter_list:
        beta = fit_approx_personal_new(filtered, h, W)
        beta_list.append(beta)
    beta_series = pd.Series(beta_list)
    var = beta_series.var()

    return var, acc, num

def load_brain_data(pkl_path, group_split=False):
    task_data = []
    id_df = pd.DataFrame()
    group1_data = []
    group2_data = []
    for filename in os.listdir(pkl_path):
        if filename.endswith(".pkl"):
            participants_filename = filename.replace("pkl", "tsv")
            participants_filename = "participants_" + participants_filename
            file_path = os.path.join(pkl_path, filename)
            participants_path = os.path.join(pkl_path, participants_filename)
            group_ids = []
            try:
                behavioral_df = pd.read_csv(participants_path, sep="\t", encoding="latin1")
                group_ids.extend(behavioral_df["dx_group"].tolist())
            except FileNotFoundError:
                behavioral_df = None
                group_ids = []
            with open(file_path, "rb") as f:
                data = pickle.load(f)
                id_df = pd.concat([id_df, pd.Series(group_ids)])
                task_data.append(data)
                if group_split and group_ids:
                    group1_data.extend([d for d, g in zip(data, group_ids) if g == 1])
                    group2_data.extend([d for d, g in zip(data, group_ids) if g == 2])
            print(f"Loaded: {filename}")
    if group_split and group1_data and group2_data:
        return group1_data, group2_data, id_df.reset_index(drop=True)
    else:
        task_data_all = [item for sublist in task_data for item in sublist]
        return task_data_all, id_df.reset_index(drop=True)

def fit_approx_personal_new(X_in, h_archetype, W_archetype, max_iter=10**3, alpha=0.9):
    beta = 1.0
    X = 2 * X_in - 1
    n, k = X.shape
    X_empirical = -0.5 * (X * (W_archetype @ X)).sum(axis=0) - h_archetype @ X
    X_empirical_mean = X_empirical.mean()
    ones_k = np.ones((1, k))
    for i in range(max_iter):
        h_term = (h_archetype * beta).reshape(-1, 1) @ ones_k
        W_term = (W_archetype * beta) @ X
        tanh_values = np.tanh(h_term + W_term)
        mean_si = tanh_values.mean(axis=1)
        si_sj = (X @ tanh_values.T) / k
        model_si_sj = (si_sj + si_sj.T) / 2
        np.fill_diagonal(model_si_sj, 0)
        H_p = -0.5 * np.sum(W_archetype * model_si_sj) - h_archetype @ mean_si
        beta -= alpha * (X_empirical_mean - H_p)
        if np.isclose(X_empirical_mean, H_p, atol=1e-6):
            break
    return beta

# ==============================================================================
# The functions below are derived from the  Energy Landscape Analysis Toolbox/Toolkit (ELAT).
# Source: https://github.com/okumakito/elapy
# Original License: Apache License Version 2.0
#
# A copy of the Apache License Version 2.0 is included in this project's LICENSE file.
# Modifications:
# - Added GPU support using PyTorch (fit_approx_GPU).
# - numpy-based implementation (fit_approx_new).
# ==============================================================================



def fit_approx_GPU(X_in: pd.DataFrame, max_iter: int = 10**3, alpha: float = 0.9):
    import torch
    device = "cuda"
    X = 2 * X_in - 1  
    n, k = X.shape
    h = torch.zeros(n,device=device)             
    W = torch.zeros((n, n),device=device)           
    X_mean = X.mean(dim=1)                        
    X_corr = (X @ X.T) / k                        
    diag = torch.arange(n, device=device)
    X_corr[diag, diag] = 0
    for _ in range(max_iter):
        Y = torch.tanh(W @ X + h.view(-1, 1))     
        h += alpha * (X_mean - Y.mean(dim=1))
        Z = (X @ Y.T) / k
        Z = 0.5 * (Z + Z.T)
        Z[diag, diag] = 0
        W += alpha * (X_corr - Z)
        if torch.allclose(X_mean, Y.mean(dim=1)) and torch.allclose(X_corr, Z):
            break
    h_cpu = h.cpu().numpy()
    W_cpu = W.cpu().numpy()
    return h, W,h_cpu,W_cpu

def fit_approx_new(X_in: pd.DataFrame, max_iter=10**3, alpha=0.9):
    X = 2 * X_in.to_numpy() - 1
    n, k = X.shape
    h = np.zeros(n)
    W = np.zeros((n, n))
    X_mean = X.mean(axis=1)
    X_corr = (X @ X.T) / k
    np.fill_diagonal(X_corr, 0)
    for _ in range(max_iter):
        Y = np.tanh(W @ X + h[:, None])
        h += alpha * (X_mean - Y.mean(axis=1))
        Z = (X @ Y.T) / k
        Z = (Z + Z.T) / 2
        np.fill_diagonal(Z, 0)
        W += alpha * (X_corr - Z)
        if np.allclose(X_mean, Y.mean(axis=1)) and np.allclose(X_corr, Z):
            break
    h_df = pd.Series(h, index=X_in.index)
    W_df = pd.DataFrame(W, index=X_in.index, columns=X_in.index)
    return h, W

def calc_state_no(X):
    return X.astype(str).sum().apply(lambda x: int(x, base=2))

def gen_all_state(X_in):
    n = len(X_in)
    X = np.array([list(bin(i)[2:].rjust(n, '0')) for i in range(2 ** n)]).astype(int).T
    return pd.DataFrame(X, index=X_in.index)

def calc_prob(h, W, X):
    energy = calc_energy(h, W, X)
    energy -= energy.min()  
    prob = np.exp(-energy)
    return prob / prob.sum()

def calc_energy(h, W, X_in):
    X = 2 * X_in - 1
    return -0.5 * (X * W.dot(X)).sum() - h.dot(X)



def calc_accuracy(h, W, X):
    freq = calc_state_no(X).value_counts()
    p_n = freq / freq.sum()
    q = X.mean(axis=1)
    X_all = gen_all_state(X)
    p_1 = (X_all.T * q + (1 - X_all).T * (1 - q)).T.prod()
    p_2 = calc_prob(h, W, X_all)
    def entropy(p):
        return (-p * np.log2(p)).sum()
    acc1 = (entropy(p_1) - entropy(p_2)) / (entropy(p_1) - entropy(p_n))
    d1 = (p_n * np.log2(p_n / p_1.iloc[p_n.index])).sum()
    d2 = (p_n * np.log2(p_n / p_2.iloc[p_n.index])).sum()
    acc2 = (d1 - d2) / d1
    return acc1, acc2

def calc_basin_graph(h, W, X):
    X_all = gen_all_state(X)
    A = calc_adjacent(X)
    energy = calc_energy(h, W, X_all)
    min_idx = energy.values[A].argmin(axis=1)
    graph = pd.DataFrame()
    graph['source'] = A.index.values
    graph['target'] = A.values[A.index, min_idx]
    graph['energy'] = energy
    G = nx.from_pandas_edgelist(graph, create_using=nx.DiGraph)
    graph['state_no'] = None
    conn = sorted(nx.weakly_connected_components(G), key=len)[::-1]
    for i, node_set in enumerate(conn):
        graph.loc[list(node_set), 'state_no'] = i + 1
    return graph, i + 1

def calc_adjacent(X):
    X_all = gen_all_state(X)
    out_list = [calc_state_no(X_all)]
    for i in X_all.index:
        Y = X_all.copy()
        Y.loc[i] = 1 - Y.loc[i]
        out_list.append(calc_state_no(Y))
    return pd.concat(out_list, axis=1)

def plot_local_min(data, graph, group, iter):
    df = graph[graph.source == graph.target]
    n = len(data)
    X = np.array([list(bin(i)[2:].rjust(n, '0')) for i in df.index]).astype(int).T
    df = pd.DataFrame(X, columns=df.state_no)
    df = df.sort_index(axis=1)

    fig, ax = plt.subplots(figsize=(4, 4))
    sns.heatmap(data=df, ax=ax, linecolor='w', lw=2, square=True,
                cmap=sns.color_palette('Paired', 2),
                cbar_kws=dict(ticks=[0.25, 0.75], shrink=0.25, aspect=2))
    ax.tick_params(length=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_title('Local minimum states', fontsize=16, pad=10)
    ax.set_xlabel('State number')
    ax.set_ylabel(None)
    cax = ax.collections[0].colorbar.ax
    cax.set_yticklabels(['0', '1'])
    cax.tick_params(length=0)
    fig.tight_layout()
    fig.show()
    
def plot_local_min_s1(data, graph):
    df = graph[graph.source == graph.target]
    n = len(data)
    X = np.array([list(bin(i)[2:].rjust(n, '0')) for i in df.index]).astype(int).T
    X_10 = np.array(df["source"])
    df = pd.DataFrame(X, index=data.index, columns=df.state_no)
    df = df.sort_index(axis=1)
    return df, X_10

