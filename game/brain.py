import numpy as np
from nn.network import NeuralNetwork


class Brain:
    def __init__(self, genome, hidden_size=6, input_size=5, num_hidden_layers=1, output_size=1):
        self._nn = NeuralNetwork.from_genome(genome, hidden_size=hidden_size, input_size=input_size, num_hidden_layers=num_hidden_layers, output_size=output_size)
        self._genome = np.array(genome, dtype=np.float64, copy=True)
        self._output_size = output_size

    def evaluate(self, inputs):
        return self._nn.forward(inputs)

    def genome(self):
        return self._genome.copy()


class ActionController:
    def __init__(self, threshold=0.5, cooldown_frames=5):
        self._threshold = threshold
        self._cooldown_frames = cooldown_frames
        self.cooldown_remaining = 0
        self._was_above_threshold = False

    def _rising_edge(self, brain_output):
        jump_val = brain_output if isinstance(brain_output, float) else brain_output[0]
        is_above = jump_val > self._threshold

        if self.cooldown_remaining > 0:
            self._was_above_threshold = is_above
            return False

        rising_edge = is_above and not self._was_above_threshold
        self._was_above_threshold = is_above

        if rising_edge:
            self.cooldown_remaining = self._cooldown_frames
            return True

        return False

    def should_jump(self, brain_output):
        return self._rising_edge(brain_output)

    def should_crouch(self, brain_output):
        if isinstance(brain_output, float):
            return False
        return float(brain_output[1]) > self._threshold

    def update(self):
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
            if self.cooldown_remaining == 0:
                self._was_above_threshold = False


class JumpController:
    def __init__(self, threshold=0.5, cooldown_frames=5):
        self._ctrl = ActionController(threshold=threshold, cooldown_frames=cooldown_frames)

    @property
    def cooldown_remaining(self):
        return self._ctrl.cooldown_remaining

    def should_jump(self, brain_output):
        return self._ctrl.should_jump(brain_output)

    def update(self):
        self._ctrl.update()
