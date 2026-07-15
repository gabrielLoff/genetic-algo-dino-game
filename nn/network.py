import numpy as np


class NeuralNetwork:
    def __init__(self, hidden_size=6, input_size=3):
        self._input_size = input_size
        self._hidden_size = hidden_size
        self._hidden_weights = np.random.randn(hidden_size, input_size) * np.sqrt(2.0 / input_size)
        self._hidden_bias = np.zeros(hidden_size)
        self._output_weights = np.random.randn(hidden_size) * np.sqrt(2.0 / hidden_size)
        self._output_bias = 0.0

    def forward(self, inputs):
        inputs = np.asarray(inputs, dtype=np.float64)
        hidden = np.maximum(0, np.dot(self._hidden_weights, inputs) + self._hidden_bias)
        raw = np.dot(self._output_weights, hidden) + self._output_bias
        return float(1.0 / (1.0 + np.exp(-raw)))

    def to_genome(self):
        return np.concatenate([
            self._hidden_weights.flatten(),
            self._hidden_bias.flatten(),
            self._output_weights.flatten(),
            np.array([self._output_bias]),
        ])

    @staticmethod
    def from_genome(genome, hidden_size=6, input_size=3):
        genome = np.asarray(genome, dtype=np.float64)
        hw_len = hidden_size * input_size
        hb_len = hidden_size
        ow_len = hidden_size

        nn = NeuralNetwork.__new__(NeuralNetwork)
        nn._input_size = input_size
        nn._hidden_size = hidden_size
        nn._hidden_weights = genome[:hw_len].reshape(hidden_size, input_size).copy()
        cursor = hw_len
        nn._hidden_bias = genome[cursor:cursor + hb_len].copy()
        cursor += hb_len
        nn._output_weights = genome[cursor:cursor + ow_len].copy()
        cursor += ow_len
        nn._output_bias = float(genome[cursor])
        return nn
