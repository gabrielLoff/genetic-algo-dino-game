import pygame
import time
from game.config import load_config, Config
from game.config_screen import ConfigScreen
from ga.evolution import Evolution, derive_seed
from dashboard.charts import compute_genome_stats
from dashboard.window import DashboardWindow
from replay.logger import LogStore
from replay.player import record_run_to_log, ReplayPlayer


def main():
    config = load_config("config.json")
    pygame.init()
    screen = pygame.display.set_mode((config.window_width, config.window_height))

    config_screen = ConfigScreen(config, screen)
    started = config_screen.run()

    if not started:
        pygame.quit()
        return

    pygame.quit()

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

        gen = evolution.generation - 1
        ms = config.master_seed
        seed = derive_seed(ms, gen) if ms is not None else gen

        if evolution.best_genome is not None:
            log = record_run_to_log(
                evolution.best_genome,
                generation=gen,
                brain_index=0, config=config,
                seed=seed,
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

    best_log = max(log_store._logs.values(), key=lambda l: l.frame_count) if log_store._logs else None

    dashboard.close()

    if best_log:
        print(f"\nReplaying best brain ({best_log.frame_count} frames)...")
        pygame.init()
        screen = pygame.display.set_mode((config.window_width, config.window_height))
        pygame.display.set_caption("GA Dino Game — Best Brain Replay")
        player = ReplayPlayer(screen)
        player.play(best_log)
        pygame.quit()

    log_store.cleanup()


if __name__ == "__main__":
    main()
