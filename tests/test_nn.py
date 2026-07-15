import numpy as np
from nn.network import NeuralNetwork


def test_nn_creates_with_he_initialization():
    nn = NeuralNetwork(hidden_size=6)
    hidden_weights = nn._hidden_weights
    hidden_bias = nn._hidden_bias

    assert hidden_weights.shape == (6, 3)
    assert hidden_bias.shape == (6,)

    std_expected = np.sqrt(2.0 / 3)
    assert abs(np.std(hidden_weights) - std_expected) < 0.5

    output_weights = nn._output_weights
    output_bias = nn._output_bias

    assert output_weights.shape == (6,)
    assert isinstance(output_bias, float)


def test_nn_forward_pass_produces_output_between_0_and_1():
    nn = NeuralNetwork(hidden_size=6)
    inputs = np.array([0.5, 0.3, 1.0])
    output = nn.forward(inputs)
    assert 0.0 <= output <= 1.0


def test_nn_forward_pass_is_deterministic():
    nn = NeuralNetwork(hidden_size=6)
    inputs = np.array([0.5, 0.3, 1.0])
    out1 = nn.forward(inputs)
    out2 = nn.forward(inputs)
    assert out1 == out2


def test_nn_configurable_hidden_size():
    nn_small = NeuralNetwork(hidden_size=4)
    nn_large = NeuralNetwork(hidden_size=10)
    assert nn_small._hidden_weights.shape == (4, 3)
    assert nn_large._hidden_weights.shape == (10, 3)


def test_to_genome_returns_flat_list_of_all_weights_and_biases():
    nn = NeuralNetwork(hidden_size=6)
    genome = nn.to_genome()
    assert isinstance(genome, np.ndarray)
    expected_len = (6 * 3) + 6 + 6 + 1
    assert len(genome) == expected_len


def test_from_genome_restores_weights_and_biases():
    nn = NeuralNetwork(hidden_size=6)
    genome = nn.to_genome()
    restored = NeuralNetwork.from_genome(genome, hidden_size=6)
    assert np.array_equal(nn._hidden_weights, restored._hidden_weights)
    assert np.array_equal(nn._hidden_bias, restored._hidden_bias)
    assert np.array_equal(nn._output_weights, restored._output_weights)
    assert nn._output_bias == restored._output_bias


def test_from_genome_preserves_forward_pass():
    nn = NeuralNetwork(hidden_size=6)
    genome = nn.to_genome()
    restored = NeuralNetwork.from_genome(genome, hidden_size=6)
    inputs = np.array([0.2, 0.7, 0.9])
    assert nn.forward(inputs) == restored.forward(inputs)


def test_genome_is_mutable_copy():
    nn = NeuralNetwork(hidden_size=6)
    genome = nn.to_genome()
    genome[0] = 999.0
    assert nn._hidden_weights[0, 0] != 999.0
