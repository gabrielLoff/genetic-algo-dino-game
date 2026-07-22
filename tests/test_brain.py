import numpy as np
from nn.network import NeuralNetwork
from game.brain import Brain, JumpController


class TestBrain:
    def test_brain_from_genome(self):
        genome = NeuralNetwork(hidden_size=6).to_genome()
        brain = Brain(genome, hidden_size=6)
        assert brain._nn is not None

    def test_brain_evaluate_returns_float(self):
        genome = NeuralNetwork(hidden_size=6).to_genome()
        brain = Brain(genome, hidden_size=6)
        inputs = np.array([0.5, 1.0, 0.3, 0.0, 0.5])
        output = brain.evaluate(inputs)
        assert isinstance(output, float)

    def test_brain_evaluate_produces_value_in_range(self):
        genome = NeuralNetwork(hidden_size=6).to_genome()
        brain = Brain(genome, hidden_size=6)
        for _ in range(100):
            inputs = np.random.random(5)
            output = brain.evaluate(inputs)
            assert 0.0 <= output <= 1.0

    def test_brain_genome_is_accessible(self):
        genome = NeuralNetwork(hidden_size=6).to_genome()
        brain = Brain(genome, hidden_size=6)
        assert len(brain.genome()) == len(genome)
        assert np.array_equal(brain.genome(), genome)


class TestJumpController:
    def test_initial_cooldown_is_zero(self):
        jc = JumpController(threshold=0.5, cooldown_frames=5)
        assert jc.cooldown_remaining == 0

    def test_no_jump_below_threshold(self):
        jc = JumpController(threshold=0.5, cooldown_frames=5)
        assert jc.should_jump(0.3) is False

    def test_jump_on_rising_edge_above_threshold(self):
        jc = JumpController(threshold=0.5, cooldown_frames=5)
        assert jc.should_jump(0.3) is False
        assert jc.should_jump(0.7) is True

    def test_no_jump_when_staying_above_threshold(self):
        jc = JumpController(threshold=0.5, cooldown_frames=5)
        jc.should_jump(0.3)
        assert jc.should_jump(0.7) is True
        assert jc.should_jump(0.8) is False  # stayed above, no rising edge
        assert jc.should_jump(0.6) is False  # still above

    def test_jump_after_falling_below_and_rising_again(self):
        jc = JumpController(threshold=0.5, cooldown_frames=2)
        jc.should_jump(0.3)
        assert jc.should_jump(0.7) is True
        jc.should_jump(0.2)  # fell below
        jc.update()
        jc.update()
        assert jc.should_jump(0.9) is True  # rising edge again after cooldown

    def test_cooldown_blocks_jump(self):
        jc = JumpController(threshold=0.5, cooldown_frames=3)
        assert jc.should_jump(0.8) is True
        jc.update()
        assert jc.cooldown_remaining == 2
        assert jc.should_jump(0.2) is False  # below threshold anyway
        jc.update()
        jc.update()
        assert jc.cooldown_remaining == 0
        assert jc.should_jump(0.3) is False
        assert jc.should_jump(0.9) is True

    def test_cooldown_decrements_each_frame(self):
        jc = JumpController(threshold=0.5, cooldown_frames=5)
        jc.should_jump(0.8)
        jc.update()
        assert jc.cooldown_remaining == 4
        jc.update()
        assert jc.cooldown_remaining == 3

    def test_rising_edge_false_when_in_cooldown(self):
        jc = JumpController(threshold=0.5, cooldown_frames=3)
        jc.should_jump(0.3)
        jc.should_jump(0.8)  # triggers jump, starts cooldown
        jc.update()
        jc.should_jump(0.2)  # fall below
        assert jc.should_jump(0.9) is False  # still in cooldown
        jc.update()
        jc.update()
        assert jc.should_jump(0.9) is True  # cooldown over, rising edge
