import numpy as np


class NeuralNetwork:
    def __init__(self, hidden_size=6, input_size=5, num_hidden_layers=1, output_size=1):
        self._input_size = input_size
        self._hidden_size = hidden_size
        self._num_hidden_layers = num_hidden_layers
        self._output_size = output_size

        self._hidden_weights = []
        self._hidden_biases = []
        prev_size = input_size
        for _ in range(num_hidden_layers):
            self._hidden_weights.append(
                np.random.randn(hidden_size, prev_size) * np.sqrt(2.0 / prev_size)
            )
            self._hidden_biases.append(np.zeros(hidden_size))
            prev_size = hidden_size

        if output_size == 1:
            self._output_weights = np.random.randn(hidden_size) * np.sqrt(2.0 / hidden_size)
            self._output_bias = 0.0
        else:
            self._output_weights = np.random.randn(output_size, hidden_size) * np.sqrt(2.0 / hidden_size)
            self._output_bias = np.zeros(output_size)

    def forward(self, inputs):
        inputs = np.asarray(inputs, dtype=np.float64)
        x = inputs
        for i in range(self._num_hidden_layers):
            x = np.maximum(0, np.dot(self._hidden_weights[i], x) + self._hidden_biases[i])
        raw = np.dot(self._output_weights, x) + self._output_bias
        result = 1.0 / (1.0 + np.exp(-raw))
        if self._output_size == 1:
            return float(result)
        return result

    def to_genome(self):
        parts = []
        for i in range(self._num_hidden_layers):
            parts.append(self._hidden_weights[i].flatten())
            parts.append(self._hidden_biases[i].flatten())
        parts.append(np.atleast_1d(np.asarray(self._output_weights, dtype=np.float64).flatten()))
        parts.append(np.atleast_1d(np.asarray(self._output_bias, dtype=np.float64).flatten()))
        return np.concatenate(parts)

    @staticmethod
    def from_genome(genome, hidden_size=6, input_size=5, num_hidden_layers=1, output_size=1):
        genome = np.asarray(genome, dtype=np.float64)
        nn = NeuralNetwork.__new__(NeuralNetwork)
        nn._input_size = input_size
        nn._hidden_size = hidden_size
        nn._num_hidden_layers = num_hidden_layers
        nn._output_size = output_size

        nn._hidden_weights = []
        nn._hidden_biases = []
        cursor = 0
        prev_size = input_size
        for _ in range(num_hidden_layers):
            w_len = hidden_size * prev_size
            nn._hidden_weights.append(
                genome[cursor:cursor + w_len].reshape(hidden_size, prev_size).copy()
            )
            cursor += w_len
            b_len = hidden_size
            nn._hidden_biases.append(genome[cursor:cursor + b_len].copy())
            cursor += b_len
            prev_size = hidden_size

        if output_size == 1:
            ow_len = hidden_size
            nn._output_weights = genome[cursor:cursor + ow_len].copy()
            cursor += ow_len
            nn._output_bias = float(genome[cursor])
        else:
            ow_len = output_size * hidden_size
            nn._output_weights = genome[cursor:cursor + ow_len].reshape(output_size, hidden_size).copy()
            cursor += ow_len
            ob_len = output_size
            nn._output_bias = genome[cursor:cursor + ob_len].copy()
        return nn

    @staticmethod
    def genome_size(hidden_size=6, input_size=5, num_hidden_layers=1, output_size=1):
        total = 0
        prev_size = input_size
        for _ in range(num_hidden_layers):
            total += hidden_size * prev_size + hidden_size
            prev_size = hidden_size
        total += hidden_size * output_size + output_size
        return total
