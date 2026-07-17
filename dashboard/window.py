import numpy as np
import matplotlib
matplotlib.use("TkAgg")
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
        self._fig, (self._ax_chart, self._ax_text) = plt.subplots(
            1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [2, 1]}
        )
        self._fig.canvas.manager.set_window_title("GA Evolution Dashboard")
        self._ax_text.axis("off")
        self._plateau_line = None

    def update(self, evolution):
        generations = [r["generation"] for r in evolution.history]
        bests = [r["best_fitness"] for r in evolution.history]
        avgs = [r["avg_fitness"] for r in evolution.history]
        cleared = [r.get("avg_cleared", 0.0) for r in evolution.history]

        self._ax_chart.clear()
        self._ax_chart.plot(generations, bests, "b-", label="Best")
        self._ax_chart.plot(generations, avgs, "r--", label="Average")
        self._ax_chart.set_xlabel("Generation")
        self._ax_chart.set_ylabel("Fitness")
        self._ax_chart.set_title(f"Generation {evolution.generation}")
        self._ax_chart.grid(True, alpha=0.3)

        ax2 = self._ax_chart.twinx()
        ax2.plot(generations, cleared, "g-o", label="Cleared", markersize=3)
        ax2.set_ylabel("Obstacles Cleared (avg)")
        ax2.grid(False)

        lines1, labels1 = self._ax_chart.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self._ax_chart.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        if evolution.end_condition == Evolution.END_PLATEAU:
            self._ax_chart.axvline(x=evolution.plateau_started_gen, color="red",
                                   linestyle="--", alpha=0.5, label="Plateau start")

        self._ax_text.clear()
        self._ax_text.axis("off")
        lines = [
            f"Generation: {evolution.generation}",
            f"Population: {evolution._config.population_size}",
            f"Best fitness: {evolution.best_fitness:.1f}",
        ]
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
        plt.pause(0.001)

    def close(self):
        plt.close(self._fig)
