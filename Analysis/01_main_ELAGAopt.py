"""
--------------------------------------------------
Tested with Python 3.13.2
--------------------------------------------------
Main script for ROI selection optimization using GA
--------------------------------------------------
Optimizes ROI selection individuals using genetic algorithm (DEAP), maximizing Ising model evaluation value.
Saves best individual, per-generation fitness, and population history.
--------------------------------------------------
"""

import random
import pandas as pd
from deap import base, creator, tools
import elagaopt as elaopt
import time
import multiprocessing
import pickle

# --- Variable settings ---
INDIVIDUAL_LENGTH = 160      # Individual length (number of ROIs)
MAX_ONES = 10                # Number of ROIs to select
POPULATION_SIZE = 100        # Population size
CROSSOVER_PROB = 1.0         # Crossover probability
MUTATION_PROB = 1.0          # Mutation probability
MAX_GENERATIONS = 1000       # Maximum number of generations
FITNESS_THRESHOLD = 10       # Optimization termination condition

# --- Path settings ---
pkl_path = "Data//test_data_1//discovery"  # Path to binarized data
output_path = "ELAGAopt_result//GA_result" # Output path
task_data_train, _ = elaopt.load_brain_data(pkl_path, group_split=False)

# --- DEAP setup --- 
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

# --- Individual initialization function ---
def init_individual():
    """
    Initialize an individual with specified number of ones and zeros
    """
    individual = [1] * MAX_ONES + [0] * (INDIVIDUAL_LENGTH - MAX_ONES)
    random.shuffle(individual)
    return creator.Individual(individual)

# --- Evaluation function ---
def evaluate_individual(individual):
    """
    Evaluation function for individual
    """
    if len(individual) != INDIVIDUAL_LENGTH:
        raise ValueError(f"Individual must have {INDIVIDUAL_LENGTH} elements.")
    result, acc, _ = elaopt.func_ELA(individual=individual, task_data_train=task_data_train,use_gpu=False)
    return result + acc,

# --- Lamarckian repair function ---
def lamarckian_repair(individual, max_ones=MAX_ONES):
    """
    Repair individual to have exactly max_ones ones
    """
    ones_idx = [i for i, x in enumerate(individual) if x == 1]
    zeros_idx = [i for i, x in enumerate(individual) if x == 0]
    if len(ones_idx) > max_ones:
        flip_indices = random.sample(ones_idx, len(ones_idx) - max_ones)
        for i in flip_indices:
            individual[i] = 0
    elif len(ones_idx) < max_ones:
        flip_indices = random.sample(zeros_idx, max_ones - len(ones_idx))
        for i in flip_indices:
            individual[i] = 1

# --- Constrained mutation function ---
def constrained_mutate(individual):
    """
    Mutate and repair individual to meet constraints
    """
    toolbox.mutate(individual)
    lamarckian_repair(individual)
    return individual

# --- Constrained crossover function ---
def constrained_mate(parent1, parent2):
    """
    Mate and repair offspring to meet constraints
    """
    toolbox.mate(parent1, parent2)
    for individual in (parent1, parent2):
        if sum(individual) != MAX_ONES:
            lamarckian_repair(individual)
    return parent1, parent2

# --- Register functions to toolbox --- 
toolbox.register("individual", init_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mutate", tools.mutFlipBit, indpb=1/INDIVIDUAL_LENGTH)
toolbox.register("constrained_mate", constrained_mate)
toolbox.register("constrained_mutate", constrained_mutate)

def main(seed):
    """
    Main function for GA optimization
    """
    random.seed(seed)
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_cores)
    toolbox.register("map", pool.map)

    # --- Initialize population ---
    population = toolbox.population(n=POPULATION_SIZE)
    pop_list, fit_list = [], []
    pop_list.append(pd.DataFrame(population))

    # --- Initial evaluation ---
    start_time = time.time()
    fitnesses = toolbox.map(toolbox.evaluate, population)
    print(f"Initial evaluation time: {time.time() - start_time:.2f} seconds")
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
    fits = [ind.fitness.values[0] for ind in population]
    fit_list.append(fits)

    # --- Track best individual ---
    generation = 0
    global_best = tools.selBest(population, 1)[0]
    best_fitness_per_gen = []
    best_ind_list = []

    # --- Evolution loop ---
    while abs(max(fits)) < FITNESS_THRESHOLD and generation < MAX_GENERATIONS:
        generation += 1
        print(f"-- Generation {generation} --")
        elites = tools.selBest(population, 1)
        offspring = list(map(toolbox.clone, toolbox.select(population, len(population)-1)))
        # --- Crossover ---
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CROSSOVER_PROB:
                toolbox.constrained_mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        # --- Mutation ---
        for mutant in offspring:
            if random.random() < MUTATION_PROB:
                toolbox.constrained_mutate(mutant)
                del mutant.fitness.values
        # --- Evaluate offspring ---
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        start_eval_time = time.time()
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # --- Update population ---
        population[:] = offspring + elites
        pop_list.append(pd.DataFrame(population))
        fits = [ind.fitness.values[0] for ind in population]
        fit_list.append(fits)
        global_best = tools.selBest(population, 1)[0]
        
        best_fitness_per_gen.append(global_best.fitness.values[0])
        best_ind_list.append(global_best)
        print(f"Best fitness in generation {generation}: {global_best.fitness.values[0]}")

    print("End of evolution")
    print(f"Best individual: {global_best}, Fitness: {global_best.fitness.values}")

    # --- Save results ---
    pd.DataFrame(best_ind_list).to_csv(f"{output_path}//best_individual//best_ind_{seed//1000}.csv", index=False)
    pd.DataFrame(best_fitness_per_gen).to_csv(f"{output_path}//objective_function//best_fitness_{seed//1000}.csv", index=False)
    with open(f"{output_path}//fitness//fitness_{seed//1000}.pkl", "wb") as f:
        pickle.dump(fit_list, f)
    with open(f"{output_path}//population//population_{seed//1000}.pkl", "wb") as f:
        pickle.dump(pop_list, f)

if __name__ == "__main__":
    # --- Run with different seeds if needed ---
    seed = 0
    for i in range(1):
        seed += 1000
        print("start:", seed)
        main(seed)