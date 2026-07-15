# Use He-initialized NeuralNetwork for genome creation

`create_population` in `ga/engine.py` delegates to `NeuralNetwork` instead of generating raw flat arrays. This is deliberate — a flat `randn() * 0.1` produces weights ~8x too small for He initialization (std ~0.1 vs std ~0.6–0.8). The consequence is every brain outputs ~0.5 on the sigmoid, producing identical behavior, zero fitness differentiation, and no evolution.

**Considered alternative:** generate flat genomes directly with per-segment standard deviations. This avoids importing the NN module into the GA engine. Rejected because it duplicates the He-init logic across two modules and creates a synchronization risk when the NN topology changes.

