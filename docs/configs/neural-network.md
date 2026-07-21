# Neural Network parameters

The Brain's topology: how many hidden layers and how many neurons per layer. These determine the function class the GA can evolve. The default is a small single-hidden-layer network — enough capacity for the dino-game policy, fast to evaluate, easy to evolve.

Topology changes propagate through the codebase via `NeuralNetwork.from_genome()` (`nn/network.py`) and `create_population()` (`ga/engine.py`). The genome encoding is flat: `[hidden_1_weights, hidden_1_bias, hidden_2_weights, hidden_2_bias, ..., output_weights, output_bias]`. For a 1-layer brain with `hidden_layer_size=6`, `output_size=1`, and 4 input features, the genome is `(6×4) + 6 + 6 + 1 = 37` values.

### `hidden_layer_size`

**Default:** 6 · **Range:** 1–100

Number of neurons in each hidden layer. All hidden layers share this size (e.g. a 3-layer brain with `hidden_layer_size=6` has layers of 6, 6, 6 neurons).

Larger networks have more capacity to learn complex input→output mappings, but each genome is longer (more parameters to evolve) and each forward pass is slower. For the dino game, 4–10 neurons is usually enough; beyond 20 you spend evolution time on diminishing returns.

**Tutorial** preset uses 4 for a quick demo.

### `num_hidden_layers`

**Default:** 1 · **Range:** 1–3

The depth of the Brain. Each additional layer adds another set of weights and biases to the genome and another ReLU stage to the forward pass (`nn/network.py:NeuralNetwork.forward`).

- **1 layer** — the default. Sufficient for most GA-evolved policies. Per-layer weights: 4 × 6 = 24.
- **2 layers** — adds capacity for hierarchical features. Total genome: `(4×6) + 6 + (6×6) + 6 + 6 + 1 = 79`.
- **3 layers** — maximum depth. Total genome: `4×6 + 6 + 6×6 + 6 + 6×6 + 6 + 6 + 1 = 121`.

Deeper networks don't guarantee better brains — the GA has to find weights that work, and a deeper search space is harder to explore.

### `output_size`

**Default:** 2 · **Range:** 1–3

Number of output neurons in the Brain. Each output represents one action:

- **1** — single output for jump only (classic dino). Total genome: 37 for a 1-layer brain with `hidden_layer_size=6`.
- **2** — two outputs: jump (index 0) and crouch (index 1). The Brain can learn to distinguish between jumping over ground-level obstacles and crouching under high-flying pterodactyls. Total genome: 44 for a 1-layer brain with `hidden_layer_size=6` (adds `6 + 1` extra output parameters per additional output neuron). Useful as a teaching example of depth vs. width in neural networks.

**Watch out for:** the genome layout changes when this changes. Code that assumes a fixed genome length will break. Use `NeuralNetwork.genome_size(hidden_size, num_hidden_layers)` to compute the expected length rather than hardcoding 37.
