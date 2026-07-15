import numpy as np


def extract_fitness_history(history):
    generations = [r["generation"] for r in history]
    bests = [r["best_fitness"] for r in history]
    avgs = [r["avg_fitness"] for r in history]
    return generations, bests, avgs


def compute_genome_stats(genome):
    return {
        "min": float(np.min(genome)),
        "max": float(np.max(genome)),
        "mean": float(np.mean(genome)),
        "std": float(np.std(genome)),
    }
