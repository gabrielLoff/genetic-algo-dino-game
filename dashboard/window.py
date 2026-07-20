import numpy as np
import matplotlib.pyplot as plt
from ga.evolution import Evolution


def compute_genome_stats(genome):
    return {
        "min": float(np.min(genome)),
        "max": float(np.max(genome)),
        "mean": float(np.mean(genome)),
        "std": float(np.std(genome)),
    }


_END_LABELS = {
    Evolution.END_MAX_GENS: "Reached max generations",
    Evolution.END_PLATEAU: "Fitness plateaued",
    Evolution.END_QUIT: "Stopped by user",
}


class DashboardWindow:
    def __init__(self):
        plt.ion()
        self._fig = plt.figure(figsize=(12, 7))
        self._fig.canvas.manager.set_window_title("GA Evolution Dashboard")
        gs = self._fig.add_gridspec(2, 2, width_ratios=[2, 1])

        self._ax_fitness = self._fig.add_subplot(gs[0, 0])
        self._ax_cleared = self._fig.add_subplot(gs[1, 0])
        self._ax_text = self._fig.add_subplot(gs[:, 1])
        self._ax_text.axis("off")

    def update(self, evolution):
        generations = [r["generation"] for r in evolution.history]
        bests = [r["best_fitness"] for r in evolution.history]
        avgs = [r["avg_fitness"] for r in evolution.history]
        cleared = [r.get("avg_cleared", 0.0) for r in evolution.history]
        diversities = [r.get("diversity", 0.0) for r in evolution.history]
        threshold = evolution._config.diversity_warning_threshold

        self._ax_fitness.clear()
        self._ax_fitness.plot(generations, bests, "b-", label="Best")
        self._ax_fitness.plot(generations, avgs, "r--", label="Average")
        self._ax_fitness.set_ylabel("Fitness")
        self._ax_fitness.set_title(f"Generation {evolution.generation}")
        self._ax_fitness.legend(loc="upper left")
        self._ax_fitness.grid(True, alpha=0.3)

        if evolution.end_condition == Evolution.END_PLATEAU:
            self._ax_fitness.axvline(x=evolution.plateau_started_gen, color="red",
                                     linestyle="--", alpha=0.5, label="Plateau start")

        for i, d in enumerate(diversities):
            if d > 0 and d < threshold:
                self._ax_fitness.axvspan(i - 0.4, i + 0.4, color="red", alpha=0.1)

        self._ax_cleared.clear()
        self._ax_cleared.plot(generations, cleared, "g-o", label="Cleared", markersize=3)
        self._ax_cleared.set_xlabel("Generation")
        self._ax_cleared.set_ylabel("Obstacles Cleared (avg)")
        self._ax_cleared.legend(loc="upper left")
        self._ax_cleared.grid(True, alpha=0.3)

        self._ax_text.clear()
        self._ax_text.axis("off")
        lines = [
            f"Generation: {evolution.generation}",
            f"Population: {evolution._config.population_size}",
            f"Best fitness: {evolution.best_fitness:.1f}",
        ]
        if diversities:
            current_div = diversities[-1]
            lines.append(f"Diversity: {current_div:.4f}")
            if current_div > 0 and current_div < threshold:
                lines.append("")
                lines.append("Low diversity -")
                lines.append("population converging")
        if evolution._config.mutation_adaptation != "none":
            eff = evolution.effective_mutation_strength
            lines.append(f"Mutation strength: {eff:.4f}")
        if evolution.end_condition != Evolution.END_RUNNING:
            label = _END_LABELS.get(evolution.end_condition, "Finished")
            lines += ["", f"Status: {label}"]
        if evolution.best_genome is not None:
            stats = compute_genome_stats(evolution.best_genome)
            lines += [
                "",
                "Best genome stats:",
                f"  Min: {stats['min']:.4f}",
                f"  Max: {stats['max']:.4f}",
                f"  Mean: {stats['mean']:.4f}",
                f"  Std: {stats['std']:.4f}",
            ]
        self._ax_text.text(0.05, 0.95, "\n".join(lines),
                           transform=self._ax_text.transAxes,
                           fontfamily="monospace", fontsize=10,
                           verticalalignment="top")

        self._fig.canvas.draw()
        self._fig.canvas.flush_events()

    def close(self):
        plt.close(self._fig)
