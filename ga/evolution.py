import hashlib
import numpy as np
from ga.engine import (
    create_population,
    tournament_select,
    uniform_crossover,
    gaussian_mutation,
    elitism_survivors,
)
from game.runner import run_generation_with_results


def derive_seed(master_seed, generation):
    key = f"{master_seed}:{generation}".encode()
    return int(hashlib.md5(key).hexdigest(), 16) % (2**31)


class Evolution:
    def __init__(self, config):
        self._config = config
        self.generation = 0
        self.history = []
        self._best_fitness = 0.0
        self._best_genome = None
        self._plateau_count = 0
        self._genome_length = self._compute_genome_length()

        np.random.seed(self._config.master_seed or np.random.randint(0, 2**31))
        self.population = create_population(
            size=self._config.population_size,
            genome_length=self._genome_length,
        )
        self._fitnesses = self._evaluate_and_track(seed=self._seed_for(0))

    def _compute_genome_length(self):
        hs = self._config.hidden_layer_size
        return (hs * 3) + hs + hs + 1

    def _seed_for(self, gen):
        ms = self._config.master_seed
        if ms is None:
            return np.random.randint(0, 2**31)
        return derive_seed(ms, gen)

    def _evaluate_and_track(self, seed):
        fitnesses, results = run_generation_with_results(
            self._config,
            self.population,
            seed=seed,
            hidden_size=self._config.hidden_layer_size,
        )
        gen_best = max(fitnesses)
        gen_avg = sum(fitnesses) / len(fitnesses)
        best_idx = fitnesses.index(gen_best)

        if gen_best > self._best_fitness:
            self._best_fitness = gen_best
            self._best_genome = self.population[best_idx].copy()
            self._plateau_count = 0
        else:
            self._plateau_count += 1

        self.history.append({
            "generation": self.generation,
            "best_fitness": gen_best,
            "avg_fitness": gen_avg,
            "best_genome": self.population[best_idx].copy(),
        })
        return fitnesses

    def step(self):
        elite_indices = elitism_survivors(
            self._fitnesses,
            elitism_rate=self._config.elitism_rate,
        )
        next_pop = [self.population[i].copy() for i in elite_indices]

        pop_size = self._config.population_size
        tournament_k = max(2, int(pop_size * self._config.tournament_size_percent))

        while len(next_pop) < pop_size:
            p1 = tournament_select(self._fitnesses, k=tournament_k)
            p2 = tournament_select(self._fitnesses, k=tournament_k)
            child = uniform_crossover(self.population[p1], self.population[p2])
            child = gaussian_mutation(
                child,
                mutation_rate=self._config.mutation_rate,
                mutation_strength=self._config.mutation_strength,
            )
            next_pop.append(child)

        self.population = next_pop
        self.generation += 1
        self._fitnesses = self._evaluate_and_track(seed=self._seed_for(self.generation))

    def is_finished(self):
        if self.generation >= self._config.max_generations:
            return True
        if self.generation > 0 and self._plateau_count >= self._config.plateau_generations:
            return True
        return False

    @property
    def best_fitness(self):
        return self._best_fitness

    @property
    def best_genome(self):
        return self._best_genome.copy() if self._best_genome is not None else None
