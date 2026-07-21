import numpy as np
from game.config import Config
from game.simulation import GameSimulation, FrameState
from nn.network import NeuralNetwork


def _make_genome():
    return NeuralNetwork(hidden_size=6).to_genome()


def _make_config(time_cap=0.05):
    config = Config()
    config.time_cap_seconds = time_cap
    config.output_size = 1
    return config


class TestObserverProtocol:
    def test_no_observers_no_callback_runs_silently(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)
        frame_count, time_alive = sim.run(observers=[])
        assert frame_count >= 0
        assert time_alive > 0

    def test_observer_called_each_frame(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        calls = []

        def observer(state):
            calls.append(state)
            return None

        sim.run(observers=[observer])
        assert len(calls) > 0

    def test_observer_receives_frame_state(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        received = []

        def observer(state):
            received.append(state)
            return None

        sim.run(observers=[observer])
        assert all(isinstance(s, FrameState) for s in received)

    def test_observer_returning_false_stops_simulation(self):
        config = _make_config(time_cap=5.0)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        def stop_after_3(state):
            if state.frame >= 3:
                return False
            return None

        frame_count, _ = sim.run(observers=[stop_after_3])
        assert frame_count == 3

    def test_observer_returning_none_continues(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        def observer(state):
            return None

        frame_count, _ = sim.run(observers=[observer])
        assert frame_count > 0

    def test_observer_returning_true_continues(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        def observer(state):
            return True

        frame_count, _ = sim.run(observers=[observer])
        assert frame_count > 0

    def test_multiple_observers_called_in_order(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        order = []

        def first(state):
            order.append("first")
            return None

        def second(state):
            order.append("second")
            return None

        sim.run(observers=[first, second])
        assert "first" in order
        assert "second" in order
        first_idx = order.index("first")
        second_idx = order.index("second")
        assert first_idx < second_idx

    def test_observer_class_with_call_method(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        class MyObserver:
            def __init__(self):
                self.count = 0

            def __call__(self, state):
                self.count += 1
                return None

        obs = MyObserver()
        sim.run(observers=[obs])
        assert obs.count > 0

    def test_legacy_per_frame_callback_still_works(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        calls = []

        def callback(state, frame, time_alive):
            calls.append((frame, time_alive))
            return None

        sim.run(callback)
        assert len(calls) > 0

    def test_observers_and_callback_combined(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        observer_calls = []
        callback_calls = []

        def observer(state):
            observer_calls.append(state)
            return None

        def callback(state, frame, time_alive):
            callback_calls.append((state, frame))
            return None

        sim.run(callback, observers=[observer])
        assert len(observer_calls) > 0
        assert len(callback_calls) > 0

    def test_observer_can_stop_before_callback(self):
        config = _make_config(time_cap=5.0)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        callback_calls = []

        def stop_after_2(state):
            if state.frame >= 2:
                return False
            return None

        def callback(state, frame, time_alive):
            callback_calls.append(frame)
            return None

        sim.run(callback, observers=[stop_after_2])
        assert max(callback_calls) <= 2

    def test_frame_state_has_frame_and_time_alive(self):
        config = _make_config(time_cap=0.05)
        genome = _make_genome()
        np.random.seed(42)
        sim = GameSimulation(config, genome, seed=42)

        seen_frame = []
        seen_time = []

        def observer(state):
            seen_frame.append(state.frame)
            seen_time.append(state.time_alive)
            return None

        sim.run(observers=[observer])
        assert seen_frame[0] == 0
        assert seen_frame[-1] == seen_frame[0] + len(seen_frame) - 1
        assert all(t >= 0 for t in seen_time)
