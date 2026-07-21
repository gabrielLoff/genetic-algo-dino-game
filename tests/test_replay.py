import json
import pygame
import numpy as np
from replay.logger import GameplayLog, FrameRecord, LogStore
from replay.player import ReplayPlayer


class TestFrameRecord:
    def test_serialize_to_dict(self):
        record = FrameRecord(
            frame=0,
            dino_y=320.0,
            obstacles=[{"x": 500.0, "size": "small"}],
            brain_output=0.3,
            game_speed=400.0,
        )
        d = record.to_dict()
        assert d["frame"] == 0
        assert d["dino_y"] == 320.0
        assert len(d["obstacles"]) == 1

    def test_from_dict_roundtrip(self):
        record = FrameRecord(
            frame=5,
            dino_y=100.0,
            obstacles=[{"x": 200.0, "size": "tall"}, {"x": 400.0, "size": "small"}],
            brain_output=0.8,
            game_speed=420.0,
        )
        d = record.to_dict()
        restored = FrameRecord.from_dict(d)
        assert restored.frame == record.frame
        assert restored.dino_y == record.dino_y
        assert restored.brain_output == record.brain_output
        assert len(restored.obstacles) == 2


class TestGameplayLog:
    def test_add_records_and_serialize(self):
        log = GameplayLog(generation=3, brain_index=0, seed=42)
        log.add(FrameRecord(0, 320.0, [], 0.1, 400.0))
        log.add(FrameRecord(1, 319.0, [{"x": 700.0, "size": "small"}], 0.6, 402.0))
        assert log.frame_count == 2

    def test_to_json(self):
        log = GameplayLog(generation=1, brain_index=0, seed=99)
        log.add(FrameRecord(0, 320.0, [], 0.0, 400.0))
        json_str = log.to_json()
        data = json.loads(json_str)
        assert data["generation"] == 1
        assert data["brain_index"] == 0
        assert data["seed"] == 99
        assert len(data["frames"]) == 1

    def test_from_json_roundtrip(self):
        log = GameplayLog(generation=2, brain_index=5, seed=7)
        log.add(FrameRecord(0, 320.0, [{"x": 600.0, "size": "tall"}], 0.9, 450.0))
        json_str = log.to_json()
        restored = GameplayLog.from_json(json_str)
        assert restored.generation == 2
        assert restored.brain_index == 5
        assert restored.seed == 7
        assert restored.frame_count == 1
        assert restored._frames[0].dino_y == 320.0


class TestLogStore:
    def test_store_and_retrieve(self):
        store = LogStore()
        log = GameplayLog(generation=1, brain_index=0, seed=42)
        log.add(FrameRecord(0, 320.0, [], 0.0, 400.0))
        store.save_best(1, log)
        retrieved = store.get_best(1)
        assert retrieved is not None
        assert retrieved.generation == 1

    def test_cleanup_clears_all(self):
        store = LogStore()
        for gen in range(5):
            log = GameplayLog(generation=gen, brain_index=0, seed=gen)
            log.add(FrameRecord(0, 320.0, [], 0.0, 400.0))
            store.save_best(gen, log)
        assert len(store._logs) == 5
        store.cleanup()
        assert len(store._logs) == 0

    def test_get_earliest_latest(self):
        store = LogStore()
        for gen in [3, 0, 7, 2]:
            log = GameplayLog(generation=gen, brain_index=0, seed=gen)
            log.add(FrameRecord(0, 320.0, [], 0.0, 400.0))
            store.save_best(gen, log)
        earliest, latest = store.get_earliest_latest()
        assert earliest.generation == 0
        assert latest.generation == 7

    def test_get_earliest_latest_empty(self):
        store = LogStore()
        earliest, latest = store.get_earliest_latest()
        assert earliest is None
        assert latest is None

    def test_get_earliest_latest_single(self):
        store = LogStore()
        log = GameplayLog(generation=5, brain_index=0, seed=5)
        log.add(FrameRecord(0, 320.0, [], 0.0, 400.0))
        store.save_best(5, log)
        earliest, latest = store.get_earliest_latest()
        assert earliest is latest


class TestReplayCompare:
    def test_play_compare_runs_without_crash(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 400))

        log0 = GameplayLog(generation=0, brain_index=0, seed=42)
        log0.add(FrameRecord(0, 320.0, [], 0.0, 400.0))
        log0.add(FrameRecord(1, 320.0, [], 0.0, 400.0))

        logN = GameplayLog(generation=10, brain_index=0, seed=42)
        logN.add(FrameRecord(0, 320.0, [], 0.5, 400.0))
        logN.add(FrameRecord(1, 310.0, [], 0.5, 400.0))
        logN.add(FrameRecord(2, 320.0, [], 0.0, 400.0))

        player = ReplayPlayer(screen)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        player.play_compare(log0, logN)
        pygame.quit()

    def test_play_compare_stops_at_shorter_log(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 400))

        log0 = GameplayLog(generation=0, brain_index=0, seed=42)
        log0.add(FrameRecord(0, 320.0, [], 0.0, 400.0))

        logN = GameplayLog(generation=10, brain_index=0, seed=42)
        logN.add(FrameRecord(0, 320.0, [], 0.5, 400.0))
        logN.add(FrameRecord(1, 310.0, [], 0.5, 400.0))
        logN.add(FrameRecord(2, 320.0, [], 0.0, 400.0))

        player = ReplayPlayer(screen)
        player.play_compare(log0, logN)
        pygame.quit()
