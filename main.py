import pygame
import time
from game.config import load_config, Config
from game.config_screen import ConfigScreen
from ga.evolution import Evolution, derive_seed
from dashboard.window import DashboardWindow, compute_genome_stats
from replay.logger import LogStore
from replay.player import record_run_to_log, ReplayPlayer


def _create_display(config):
    flags = pygame.NOFRAME if config.fullscreen else 0
    if config.fullscreen:
        info = pygame.display.Info()
        return pygame.display.set_mode((info.current_w, info.current_h), flags)
    return pygame.display.set_mode((config.window_width, config.window_height), flags)


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


def _record_ghosts(evolution, config, log_store):
    if config.ghost_mode == "off":
        return
    gen = evolution.generation - 1
    ms = config.master_seed
    seed = derive_seed(ms, gen) if ms is not None else gen
    fitnesses = evolution._fitnesses
    pop = evolution.population

    if config.ghost_mode == "worst":
        worst_idx = fitnesses.index(min(fitnesses))
        if worst_idx == fitnesses.index(max(fitnesses)):
            return
        log = record_run_to_log(pop[worst_idx], generation=gen,
                                brain_index=worst_idx, config=config, seed=seed)
        if log.frame_count > 0:
            log_store.save_ghosts(gen, [log], ["Worst"])

    elif config.ghost_mode == "random":
        candidates = [i for i in range(len(fitnesses)) if i != fitnesses.index(max(fitnesses))]
        if not candidates:
            return
        idx = candidates[hash(str(seed)) % len(candidates)]
        log = record_run_to_log(pop[idx], generation=gen,
                                brain_index=idx, config=config, seed=seed)
        if log.frame_count > 0:
            log_store.save_ghosts(gen, [log], ["Random"])

    elif config.ghost_mode == "top":
        sorted_idx = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
        ghost_indices = sorted_idx[1:1 + config.ghost_count]
        ghost_logs = []
        ghost_labels = []
        for rank, idx in enumerate(ghost_indices, start=2):
            log = record_run_to_log(pop[idx], generation=gen,
                                    brain_index=idx, config=config, seed=seed)
            if log.frame_count > 0:
                ghost_logs.append(log)
                ghost_labels.append(f"#{rank}")
        if ghost_logs:
            log_store.save_ghosts(gen, ghost_logs, ghost_labels)


def _replay_best(config, log_store):
    if not log_store._logs:
        print("No replays available.")
        return
    best_log = max(log_store._logs.values(), key=lambda l: l.frame_count)
    gen = best_log.generation
    ghosts, ghost_labels = log_store.get_ghosts_and_labels(gen)
    print(f"Replaying best brain ({best_log.frame_count} frames)... Press SPACE to stop.")
    pygame.init()
    screen = _create_display(config)
    pygame.display.set_caption("GA Dino Game — Best Brain Replay")
    ReplayPlayer(screen).play(best_log, ghost_logs=ghosts, ghost_labels=ghost_labels)
    pygame.quit()


def _replay_compare(config, log_store):
    gen0_log, genN_log = log_store.get_earliest_latest()
    if gen0_log is None or genN_log is None or gen0_log.generation == genN_log.generation:
        print("Need at least 2 generations for comparison replay.")
        return
    print(f"Comparing Gen {gen0_log.generation} vs Gen {genN_log.generation} "
          f"({gen0_log.frame_count} vs {genN_log.frame_count} frames)...")
    pygame.init()
    screen = _create_display(config)
    pygame.display.set_caption("GA Dino Game — Generation Comparison")
    ReplayPlayer(screen).play_compare(gen0_log, genN_log)
    pygame.quit()


def _run_evolution(config, log_store, interactive=True):
    evolution = Evolution(config)
    dashboard = DashboardWindow()

    print(f"Gen {evolution.history[-1]['generation']:3d} | "
          f"best={evolution.history[-1]['best_fitness']:8.1f} "
          f"avg={evolution.history[-1]['avg_fitness']:8.1f}")
    dashboard.update(evolution)

    remaining = 0

    while not evolution.is_finished():
        evolution.step()
        dashboard.update(evolution)

        if evolution.best_genome is not None:
            _record_best(evolution, config, log_store)
            _record_ghosts(evolution, config, log_store)

        last = evolution.history[-1]
        print(f"Gen {last['generation']:3d} | best={last['best_fitness']:8.1f} "
              f"avg={last['avg_fitness']:8.1f}")

        if not interactive:
            continue

        remaining -= 1
        if remaining > 0 and not evolution.is_finished():
            continue

        print("[Enter=next gen | N=run N more | R=replay best | C=compare gens | Q=quit]")
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "":
                remaining = 0
                break
            elif cmd == "q":
                remaining = 0
                evolution.stop(Evolution.END_QUIT)
                break
            elif cmd == "r":
                _replay_best(config, log_store)
                print("[Enter=next gen | N=run N more | R=replay best | C=compare gens | Q=quit]")
            elif cmd == "c":
                _replay_compare(config, log_store)
                print("[Enter=next gen | N=run N more | R=replay best | C=compare gens | Q=quit]")
            elif cmd.isdigit():
                remaining = int(cmd) - 1
                break
            else:
                print("Unknown command. Enter=next, N=run N, R=replay, C=compare, Q=quit")

    reason = evolution.end_condition

    if reason == Evolution.END_PLATEAU:
        print(f"Evolution finished after {evolution.generation} generations "
              f"(plateau since gen {evolution.plateau_started_gen})")
    elif reason == Evolution.END_MAX_GENS:
        print(f"Evolution finished after {evolution.generation} generations "
              f"(reached max_generations)")
    elif reason == Evolution.END_QUIT:
        print(f"Evolution stopped by user after {evolution.generation} generations")
    else:
        print(f"Evolution finished after {evolution.generation} generations")

    dashboard.close()
    return evolution


def _compare_evolutions(preset_a, preset_b):
    from game.presets import apply_preset

    print("\n" + "=" * 70)
    print("COMPARISON MODE")
    print("=" * 70)

    config_a = Config()
    apply_preset(config_a, preset_a)
    log_store_a = LogStore()
    print(f"\n--- Running Preset A: {preset_a['name']} ---")
    print(f"    {preset_a['description']}")
    print(f"    pop={config_a.population_size} mut={config_a.mutation_rate} "
          f"fitness={config_a.fitness_function} gens={config_a.max_generations}")
    start_a = time.perf_counter()
    evo_a = _run_evolution(config_a, log_store_a, interactive=False)
    elapsed_a = time.perf_counter() - start_a
    log_store_a.cleanup()

    config_b = Config()
    apply_preset(config_b, preset_b)
    log_store_b = LogStore()
    print(f"\n--- Running Preset B: {preset_b['name']} ---")
    print(f"    {preset_b['description']}")
    print(f"    pop={config_b.population_size} mut={config_b.mutation_rate} "
          f"fitness={config_b.fitness_function} gens={config_b.max_generations}")
    start_b = time.perf_counter()
    evo_b = _run_evolution(config_b, log_store_b, interactive=False)
    elapsed_b = time.perf_counter() - start_b

    best_a = evo_a.best_fitness
    best_b = evo_b.best_fitness
    gens_a = evo_a.generation
    gens_b = evo_b.generation
    end_a = evo_a.end_condition
    end_b = evo_b.end_condition

    winner = "A" if best_a > best_b else "B" if best_b > best_a else "tie"

    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    print(f"  {'':20s} {'Preset A':>20s} {'Preset B':>20s}")
    print(f"  {'':20s} {'-------':>20s} {'-------':>20s}")
    print(f"  {'Name':20s} {preset_a['name']:>20s} {preset_b['name']:>20s}")
    print(f"  {'Best Fitness':20s} {best_a:>20.1f} {best_b:>20.1f}")
    print(f"  {'Generations':20s} {gens_a:>20d} {gens_b:>20d}")
    print(f"  {'End Condition':20s} {end_a:>20s} {end_b:>20s}")
    print(f"  {'Duration (s)':20s} {elapsed_a:>20.1f} {elapsed_b:>20.1f}")
    print(f"  {'Winner':20s} {winner:>20s}")
    print("=" * 60)

    return evo_b, log_store_b


def main():
    import matplotlib
    matplotlib.use("TkAgg")
    config = load_config("config.json")
    pygame.init()
    screen = _create_display(config)

    config_screen = ConfigScreen(config, screen)
    started = config_screen.run()
    pygame.quit()

    if not started:
        return

    print(f"Starting evolution: population={config.population_size}, "
          f"max_generations={config.max_generations}, "
          f"fitness={config.fitness_function}")

    log_store = LogStore()

    comparison_presets = config_screen.comparison_presets
    if comparison_presets:
        preset_a, preset_b = comparison_presets
        evolution, log_store = _compare_evolutions(preset_a, preset_b)
    else:
        evolution = _run_evolution(config, log_store)

    if evolution.best_genome is not None:
        stats = compute_genome_stats(evolution.best_genome)
        print(f"Best fitness: {evolution.best_fitness:.1f}")
        print(f"Best genome: min={stats['min']:.4f} max={stats['max']:.4f} "
              f"mean={stats['mean']:.4f} std={stats['std']:.4f}")

    _replay_best(config, log_store)
    log_store.cleanup()


if __name__ == "__main__":
    main()
