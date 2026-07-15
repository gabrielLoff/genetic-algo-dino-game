import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from dashboard.charts import extract_fitness_history, compute_genome_stats


class DashboardWindow:
    def __init__(self):
        plt.ion()
        self._fig, (self._ax_chart, self._ax_text) = plt.subplots(
            1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [2, 1]}
        )
        self._fig.canvas.manager.set_window_title("GA Evolution Dashboard")
        self._ax_text.axis("off")

    def update(self, evolution):
        generations, bests, avgs = extract_fitness_history(evolution.history)

        self._ax_chart.clear()
        self._ax_chart.plot(generations, bests, "b-", label="Best")
        self._ax_chart.plot(generations, avgs, "r--", label="Average")
        self._ax_chart.set_xlabel("Generation")
        self._ax_chart.set_ylabel("Fitness")
        self._ax_chart.set_title(f"Generation {evolution.generation}")
        self._ax_chart.legend(loc="upper left")
        self._ax_chart.grid(True, alpha=0.3)

        self._ax_text.clear()
        self._ax_text.axis("off")
        lines = [
            f"Generation: {evolution.generation}",
            f"Population: {evolution._config.population_size}",
            f"Best fitness: {evolution.best_fitness:.1f}",
        ]
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
