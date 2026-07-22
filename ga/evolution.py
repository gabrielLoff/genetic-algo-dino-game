import hashlib
import numpy as np
from ga.engine import (
    create_population,
    tournament_select,
    uniform_crossover,
    single_point_crossover,
    two_point_crossover,
    gaussian_mutation,
    elitism_survivors,
)

_CROSSOVER_MAP = {
    "uniform": uniform_crossover,
    "single_point": single_point_crossover,
    "two_point": two_point_crossover,
}


def derive_seed(master_seed, generation):
    key = f"{master_seed}:{generation}".encode()
    return int(hashlib.md5(key).hexdigest(), 16) % (2**31)


def compute_weight_diff(old_genome, new_genome, hidden_size, input_size=5, num_hidden_layers=1, output_size=1):
    diff = np.asarray(new_genome, dtype=np.float64) - np.asarray(old_genome, dtype=np.float64)
    sigma = float(np.std(np.abs(diff)))
    abs_diff = np.abs(diff)

    groups = {}
    cursor = 0
    prev_size = input_size
    for i in range(num_hidden_layers):
        w_len = hidden_size * prev_size
        groups[f"hidden_{i+1}_weights"] = {
            "count": int(np.sum(abs_diff[cursor:cursor + w_len] > sigma)),
            "total": w_len,
        }
        cursor += w_len
        b_len = hidden_size
        groups[f"hidden_{i+1}_bias"] = {
            "count": int(np.sum(abs_diff[cursor:cursor + b_len] > sigma)),
            "total": b_len,
        }
        cursor += b_len
        prev_size = hidden_size

    o_len = hidden_size * output_size
    groups["output_weights"] = {
        "count": int(np.sum(abs_diff[cursor:cursor + o_len] > sigma)),
        "total": o_len,
    }
    return groups


class Evolution:
    END_RUNNING = "running"
    END_MAX_GENS = "max_generations"
    END_PLATEAU = "plateau"
    END_QUIT = "quit"

    def __init__(self, config, evaluator=None):
        if evaluator is None:
            from game.runner import run_generation
            evaluator = run_generation
        self._config = config
        self._evaluator = evaluator
        self.generation = 0
        self.history = []
        self._best_fitness = 0.0
        self._best_genome = None
        self._plateau_count = 0
        self._plateau_started_gen = 0
        self._end_condition = self.END_RUNNING
        self._curriculum_tier = 0

        np.random.seed(self._config.master_seed or np.random.randint(0, 2**31))
        self.population = create_population(
            size=self._config.population_size,
            hidden_size=self._config.hidden_layer_size,
            input_size=5,
            num_hidden_layers=self._config.num_hidden_layers,
            output_size=self._config.output_size,
        )
        self._fitnesses = self._evaluate_and_track(seed=self._seed_for(0))

    def _seed_for(self, gen):
        ms = self._config.master_seed
        if ms is None:
            return np.random.randint(0, 2**31)
        return derive_seed(ms, gen)

    def _compute_diversity(self):
        if len(self.population) < 2:
            return 0.0
        genomes = np.array(self.population)
        genome_len = genomes.shape[1]
        sample = genomes[:min(50, len(genomes))]
        diff = sample[:, None, :] - sample[None, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=-1))
        triu = np.triu(distances, k=1)
        nonzero = triu[triu > 0]
        if len(nonzero) == 0:
            return 0.0
        return float(np.mean(nonzero) / genome_len)

    def _update_curriculum_tier(self):
        if not self._config.curriculum_mode:
            self._curriculum_tier = 0
            self._config.curriculum_tier = 0
            return
        theoretical_max = self._config.time_cap_seconds * self._config.game_speed_initial
        tier1 = theoretical_max * 0.25
        tier2 = theoretical_max * 0.50
        if self._best_fitness < tier1:
            self._curriculum_tier = 0
        elif self._best_fitness < tier2:
            self._curriculum_tier = 1
        else:
            self._curriculum_tier = 2
        self._config.curriculum_tier = self._curriculum_tier

    def _evaluate_and_track(self, seed):
        self._update_curriculum_tier()
        fitnesses, results = self._evaluator(
            self._config,
            self.population,
            seed=seed,
            hidden_size=self._config.hidden_layer_size,
        )
        gen_best = max(fitnesses)
        gen_avg = sum(fitnesses) / len(fitnesses)
        best_idx = fitnesses.index(gen_best)

        cleared = [r.obstacles_cleared for r in results]
        avg_cleared = sum(cleared) / len(cleared) if cleared else 0.0
        diversity = self._compute_diversity()

        if gen_best > self._best_fitness:
            old_best = self._best_fitness
            old_genome = self._best_genome
            self._best_fitness = gen_best
            self._best_genome = self.population[best_idx].copy()
            self._plateau_count = 0
            self._plateau_started_gen = self.generation + 1
            if old_genome is not None:
                self._print_weight_diff(old_genome, self._best_genome, old_best, gen_best)
        else:
            self._plateau_count += 1

        self.history.append({
            "generation": self.generation,
            "best_fitness": gen_best,
            "avg_fitness": gen_avg,
            "best_genome": self.population[best_idx].copy(),
            "avg_cleared": avg_cleared,
            "diversity": diversity,
            "curriculum_tier": self._curriculum_tier,
        })
        return fitnesses

    def _print_weight_diff(self, old_genome, new_genome, old_fitness, new_fitness):
        diff = compute_weight_diff(
            old_genome, new_genome,
            hidden_size=self._config.hidden_layer_size,
            input_size=5,
            num_hidden_layers=self._config.num_hidden_layers,
            output_size=self._config.output_size,
        )
        delta = new_fitness - old_fitness
        print(
            f"Gen {self.generation}: best fitness "
            f"{old_fitness:.1f} -> {new_fitness:.1f} (+{delta:.1f})"
        )
        for group, info in diff.items():
            print(f"  {group}: {info['count']} of {info['total']} shifted >1σ")

    def _effective_mutation_strength(self, diversity=None):
        if self._config.mutation_adaptation == "none":
            return self._config.mutation_strength

        if diversity is None:
            diversity = 0.0
            if self.history:
                diversity = self.history[-1].get("diversity", 0.0)

        if self._config.mutation_adaptation == "linear_decay":
            progress = self.generation / max(self._config.max_generations, 1)
            return max(
                self._config.mutation_strength * (1.0 - progress),
                self._config.mutation_strength_floor,
            )
        elif self._config.mutation_adaptation == "diversity_driven":
            threshold = max(self._config.diversity_warning_threshold, 1e-6)
            raw = self._config.mutation_strength * (threshold / max(diversity, 1e-6))
            return max(
                min(raw, self._config.mutation_strength_cap),
                self._config.mutation_strength_floor,
            )

        return self._config.mutation_strength

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
            crossover_fn = _CROSSOVER_MAP.get(self._config.crossover_operator, uniform_crossover)
            child = crossover_fn(self.population[p1], self.population[p2])
            effective_strength = self._effective_mutation_strength()
            child = gaussian_mutation(
                child,
                mutation_rate=self._config.mutation_rate,
                mutation_strength=effective_strength,
            )
            next_pop.append(child)

        self.population = next_pop
        self.generation += 1
        self._fitnesses = self._evaluate_and_track(seed=self._seed_for(self.generation))

        if self.generation >= self._config.max_generations:
            self._end_condition = self.END_MAX_GENS
        elif self.generation > 0 and self._plateau_count >= self._config.plateau_generations:
            self._end_condition = self.END_PLATEAU

    def is_finished(self):
        return self._end_condition != self.END_RUNNING

    def stop(self, reason):
        if reason in (self.END_QUIT, self.END_PLATEAU, self.END_MAX_GENS):
            self._end_condition = reason

    @property
    def end_condition(self):
        return self._end_condition

    @property
    def plateau_started_gen(self):
        return self._plateau_started_gen

    @property
    def best_fitness(self):
        return self._best_fitness

    @property
    def best_genome(self):
        return self._best_genome.copy() if self._best_genome is not None else None

    @property
    def effective_mutation_strength(self):
        return self._effective_mutation_strength()

    @property
    def curriculum_tier(self):
        return self._curriculum_tier
