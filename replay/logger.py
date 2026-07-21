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
    def __init__(self, generation, brain_index, seed):
        self.generation = generation
        self.brain_index = brain_index
        self.seed = seed
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
            "frames": [f.to_dict() for f in self._frames],
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        log = GameplayLog(
            generation=data["generation"],
            brain_index=data["brain_index"],
            seed=data["seed"],
        )
        for frame_data in data["frames"]:
            log.add(FrameRecord.from_dict(frame_data))
        return log

    @property
    def frames(self):
        return list(self._frames)


class LogStore:
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

    def cleanup(self):
        self._logs.clear()
        self._ghost_logs.clear()
        self._ghost_labels.clear()
