import numpy as np


def create_population(size, genome_length):
    return [np.random.randn(genome_length) * 0.1 for _ in range(size)]


def tournament_select(fitnesses, k):
    indices = np.random.choice(len(fitnesses), size=k, replace=False)
    best_idx = indices[0]
    for i in indices:
        if fitnesses[i] > fitnesses[best_idx]:
            best_idx = i
    return best_idx


def uniform_crossover(parent_a, parent_b):
    mask = np.random.random(len(parent_a)) < 0.5
    child = np.where(mask, parent_a, parent_b)
    return child


def gaussian_mutation(genome, mutation_rate, mutation_strength):
    mutated = np.array(genome, dtype=np.float64, copy=True)
    mask = np.random.random(len(mutated)) < mutation_rate
    noise = np.random.randn(np.sum(mask)) * mutation_strength
    mutated[mask] += noise
    return mutated


def elitism_survivors(fitnesses, elitism_rate):
    n_elite = max(1, int(len(fitnesses) * elitism_rate))
    sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    return sorted_indices[:n_elite]
