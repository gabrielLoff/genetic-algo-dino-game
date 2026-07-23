from ga.evolution import Evolution


def narrate_generation(evolution, config):
    if not config.narrated_mode:
        return

    history = evolution.history
    if not history:
        print("Narrator: No evolution data yet.")
        return

    last = history[-1]
    gen = last.generation
    best = last.best_fitness
    avg = last.avg_fitness
    avg_cleared = last.avg_cleared

    best_time = best / max(config.game_speed_initial, 1)
    avg_time = avg / max(config.game_speed_initial, 1)
    best_obs = int(best_time * 0.5)

    parts = [
        f"Generation {gen}: "
        f"The best brain scored {best:.0f} fitness "
        f"(survived ~{best_time:.1f}s, cleared ~{best_obs} obstacles). "
        f"The average brain scored {avg:.0f} fitness "
        f"(~{avg_time:.1f}s)."
    ]

    if gen > 0:
        prev_best = history[0].best_fitness
        improvement = best - prev_best
        if improvement > 0:
            parts.append(f" Fitness has improved {improvement:.0f} points since generation 0.")
        else:
            parts.append(" No improvement since generation 0 yet.")

    if avg_cleared > 0:
        parts.append(f" Average obstacles cleared per brain: {avg_cleared:.1f}.")

    if evolution._plateau_count >= max(config.plateau_generations // 2, 1):
        parts.append(
            f" Best fitness has not improved for {evolution._plateau_count} generations. "
            "Evolution may be stalling."
        )

    if evolution.end_condition == Evolution.END_MAX_GENS:
        parts.append(
            f"We have reached {config.max_generations} generations. "
            "The best brain has learned to consistently jump over obstacles."
        )
    elif evolution.end_condition == Evolution.END_PLATEAU:
        parts.append(
            f"Evolution stopped: no improvement for {config.plateau_generations} generations."
        )

    print("Narrator: " + "".join(parts))
