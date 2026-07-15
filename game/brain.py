import numpy as np
from nn.network import NeuralNetwork


class Brain:
    def __init__(self, genome, hidden_size=6, input_size=3):
        self._nn = NeuralNetwork.from_genome(genome, hidden_size=hidden_size, input_size=input_size)
        self._genome = np.array(genome, dtype=np.float64, copy=True)

    def evaluate(self, inputs):
        return self._nn.forward(inputs)

    def genome(self):
        return self._genome.copy()


class JumpController:
    def __init__(self, threshold=0.5, cooldown_frames=5):
        self._threshold = threshold
        self._cooldown_frames = cooldown_frames
        self.cooldown_remaining = 0
        self._was_above_threshold = False

    def should_jump(self, brain_output):
        is_above = brain_output > self._threshold

        if self.cooldown_remaining > 0:
            self._was_above_threshold = is_above
            return False

        rising_edge = is_above and not self._was_above_threshold
        self._was_above_threshold = is_above

        if rising_edge:
            self.cooldown_remaining = self._cooldown_frames
            return True

        return False

    def update(self):
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
            if self.cooldown_remaining == 0:
                self._was_above_threshold = False
