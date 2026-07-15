from game.config import load_config
from ga.evolution import Evolution
from dashboard.charts import extract_fitness_history, compute_genome_stats
from dashboard.window import DashboardWindow
from replay.logger import LogStore
from replay.player import record_run_to_log
import time


def main():
    config = load_config("config.json")
    print(f"Starting evolution: population={config.population_size}, "
          f"max_generations={config.max_generations}, "
          f"fitness={config.fitness_function}")

    evolution = Evolution(config)
    dashboard = DashboardWindow()
    log_store = LogStore()

    print(f"Gen {evolution.history[-1]['generation']:3d} | "
          f"best={evolution.history[-1]['best_fitness']:8.1f} "
          f"avg={evolution.history[-1]['avg_fitness']:8.1f}")
    dashboard.update(evolution)

    start = time.perf_counter()

    while not evolution.is_finished():
        evolution.step()
        dashboard.update(evolution)

        if evolution.best_genome is not None:
            best_idx = evolution.history[-1].get("best_genome")
            if best_idx is not None:
                log = record_run_to_log(
                    evolution, evolution.best_genome,
                    generation=evolution.generation - 1,
                    brain_index=0, config=config,
                )
                if log.frame_count > 0:
                    log_store.save_best(evolution.generation - 1, log)

        last = evolution.history[-1]
        print(f"Gen {last['generation']:3d} | best={last['best_fitness']:8.1f} "
              f"avg={last['avg_fitness']:8.1f}")

    elapsed = time.perf_counter() - start
    print(f"\nEvolution finished in {elapsed:.1f}s after {evolution.generation} generations")
    print(f"Best fitness: {evolution.best_fitness:.1f}")

    if evolution.best_genome is not None:
        stats = compute_genome_stats(evolution.best_genome)
        print(f"Best genome: min={stats['min']:.4f} max={stats['max']:.4f} "
              f"mean={stats['mean']:.4f} std={stats['std']:.4f}")

    print(f"\nReplays recorded for {len(log_store._logs)} generations")

    input("\nPress Enter to close dashboard...")
    dashboard.close()
    log_store.cleanup()


if __name__ == "__main__":
    main()
