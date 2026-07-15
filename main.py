import pygame
import time
from game.config import load_config, Config
from game.config_screen import ConfigScreen
from ga.evolution import Evolution, derive_seed
from dashboard.charts import compute_genome_stats
from dashboard.window import DashboardWindow
from replay.logger import LogStore
from replay.player import record_run_to_log, ReplayPlayer


def _record_best(evolution, config, log_store):
    gen = evolution.generation - 1
    ms = config.master_seed
    seed = derive_seed(ms, gen) if ms is not None else gen
    log = record_run_to_log(
        evolution.best_genome, generation=gen,
        brain_index=0, config=config, seed=seed,
    )
    if log.frame_count > 0:
        log_store.save_best(gen, log)


def _replay_best(config, log_store):
    if not log_store._logs:
        print("No replays available.")
        return
    best_log = max(log_store._logs.values(), key=lambda l: l.frame_count)
    print(f"Replaying best brain ({best_log.frame_count} frames)... Press SPACE to stop.")
    pygame.init()
    screen = pygame.display.set_mode((config.window_width, config.window_height))
    pygame.display.set_caption("GA Dino Game — Best Brain Replay")
    ReplayPlayer(screen).play(best_log)
    pygame.quit()


def main():
    config = load_config("config.json")
    pygame.init()
    screen = pygame.display.set_mode((config.window_width, config.window_height))

    config_screen = ConfigScreen(config, screen)
    started = config_screen.run()
    pygame.quit()

    if not started:
        return

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

    remaining = 0
    start = time.perf_counter()

    while not evolution.is_finished():
        evolution.step()
        dashboard.update(evolution)

        if evolution.best_genome is not None:
            _record_best(evolution, config, log_store)

        last = evolution.history[-1]
        print(f"Gen {last['generation']:3d} | best={last['best_fitness']:8.1f} "
              f"avg={last['avg_fitness']:8.1f}")

        remaining -= 1
        if remaining > 0 and not evolution.is_finished():
            continue

        print("[Enter=next gen | N=run N more | R=replay best | Q=quit]")
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "":
                remaining = 0
                break
            elif cmd == "q":
                remaining = 0
                evolution._plateau_count = config.plateau_generations + 1
                break
            elif cmd == "r":
                _replay_best(config, log_store)
                print("[Enter=next gen | N=run N more | R=replay best | Q=quit]")
            elif cmd.isdigit():
                remaining = int(cmd) - 1
                break
            else:
                print("Unknown command. Enter=next, N=run N, R=replay, Q=quit")

    elapsed = time.perf_counter() - start
    print(f"\nEvolution finished in {elapsed:.1f}s after {evolution.generation} generations")
    print(f"Best fitness: {evolution.best_fitness:.1f}")

    if evolution.best_genome is not None:
        stats = compute_genome_stats(evolution.best_genome)
        print(f"Best genome: min={stats['min']:.4f} max={stats['max']:.4f} "
              f"mean={stats['mean']:.4f} std={stats['std']:.4f}")

    dashboard.close()
    _replay_best(config, log_store)
    log_store.cleanup()


if __name__ == "__main__":
    main()
