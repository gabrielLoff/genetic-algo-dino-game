import json


class FrameRecord:
    def __init__(self, frame, dino_y, obstacles, brain_output, game_speed, is_crouching=False):
        self.frame = frame
        self.dino_y = dino_y
        self.obstacles = obstacles
        self.brain_output = brain_output
        self.game_speed = game_speed
        self.is_crouching = is_crouching

    def to_dict(self):
        return {
            "frame": self.frame,
            "dino_y": self.dino_y,
            "obstacles": self.obstacles,
            "brain_output": self.brain_output,
            "game_speed": self.game_speed,
            "is_crouching": self.is_crouching,
        }

    @staticmethod
    def from_dict(d):
        return FrameRecord(
            frame=d["frame"],
            dino_y=d["dino_y"],
            obstacles=d["obstacles"],
            brain_output=d["brain_output"],
            game_speed=d["game_speed"],
            is_crouching=d.get("is_crouching", False),
        )


class GameplayLog:
    def __init__(self, generation, brain_index, seed, fitness=0.0):
        self.generation = generation
        self.brain_index = brain_index
        self.seed = seed
        self.fitness = fitness
        self._frames = []

    def add(self, record):
        self._frames.append(record)

    @property
    def frame_count(self):
        return len(self._frames)

    def to_json(self):
        return json.dumps({
            "generation": self.generation,
            "brain_index": self.brain_index,
            "seed": self.seed,
            "fitness": self.fitness,
            "frames": [f.to_dict() for f in self._frames],
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        log = GameplayLog(
            generation=data["generation"],
            brain_index=data["brain_index"],
            seed=data["seed"],
            fitness=data.get("fitness", 0.0),
        )
        for frame_data in data["frames"]:
            log.add(FrameRecord.from_dict(frame_data))
        return log

    @property
    def frames(self):
        return list(self._frames)


class GenerationArchive:
    def __init__(self):
        self._logs = {}
        self._ghost_logs = {}
        self._ghost_labels = {}

    def save_best(self, generation, log):
        self._logs[generation] = log

    def get_best(self, generation):
        return self._logs.get(generation)

    def save_ghosts(self, generation, ghost_logs, labels):
        self._ghost_logs[generation] = ghost_logs
        self._ghost_labels[generation] = labels

    def get_ghosts_and_labels(self, generation):
        return (
            self._ghost_logs.get(generation, []),
            self._ghost_labels.get(generation, []),
        )

    def get_earliest_latest(self):
        if not self._logs:
            return None, None
        sorted_gens = sorted(self._logs.keys())
        return self._logs[sorted_gens[0]], self._logs[sorted_gens[-1]]

    def best_frames_available(self):
        return len(self._logs) > 0

    def best_log_by_frame_count(self):
        if not self._logs:
            return None
        return max(self._logs.values(), key=lambda l: l.frame_count)

    def record_best(self, evolution, config):
        from replay.player import record_run_to_log
        from ga.evolution import derive_seed

        gen = evolution.generation - 1
        ms = config.master_seed
        seed = derive_seed(ms, gen) if ms is not None else gen
        fitness = evolution.history[-1]["best_fitness"]
        log = record_run_to_log(
            evolution.best_genome, generation=gen,
            brain_index=0, config=config, seed=seed, fitness=fitness,
        )
        if log.frame_count > 0:
            self.save_best(gen, log)

    def record_ghosts(self, evolution, config):
        from replay.player import record_run_to_log
        from ga.evolution import derive_seed

        mode = config.ghost_mode
        if mode == "off":
            return
        gen = evolution.generation - 1
        ms = config.master_seed
        seed = derive_seed(ms, gen) if ms is not None else gen
        fitnesses = evolution._fitnesses
        pop = evolution.population

        if mode == "worst":
            worst_idx = fitnesses.index(min(fitnesses))
            if worst_idx == fitnesses.index(max(fitnesses)):
                return
            log = record_run_to_log(pop[worst_idx], generation=gen,
                                    brain_index=worst_idx, config=config, seed=seed,
                                    fitness=fitnesses[worst_idx])
            if log.frame_count > 0:
                self.save_ghosts(gen, [log], ["Worst"])

        elif mode == "random":
            candidates = [i for i in range(len(fitnesses)) if i != fitnesses.index(max(fitnesses))]
            if not candidates:
                return
            idx = candidates[hash(str(seed)) % len(candidates)]
            log = record_run_to_log(pop[idx], generation=gen,
                                    brain_index=idx, config=config, seed=seed,
                                    fitness=fitnesses[idx])
            if log.frame_count > 0:
                self.save_ghosts(gen, [log], ["Random"])

        elif mode == "top":
            sorted_idx = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
            ghost_indices = sorted_idx[1:1 + config.ghost_count]
            ghost_logs = []
            ghost_labels = []
            for rank, idx in enumerate(ghost_indices, start=2):
                log = record_run_to_log(pop[idx], generation=gen,
                                        brain_index=idx, config=config, seed=seed,
                                        fitness=fitnesses[idx])
                if log.frame_count > 0:
                    ghost_logs.append(log)
                    ghost_labels.append(f"#{rank}")
            if ghost_logs:
                self.save_ghosts(gen, ghost_logs, ghost_labels)

    def cleanup(self):
        self._logs.clear()
        self._ghost_logs.clear()
        self._ghost_labels.clear()


LogStore = GenerationArchive
