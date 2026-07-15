# Genetic Algorithm Dino Game

A replica of the Google Chrome Dino Game used to demonstrate a genetic algorithm (neuroevolution) in action — brains evolve over generations to learn when and how hard to jump.

## Language

### Lifecycle

**Frame**:
A single tick of the game loop. Physics update + brain evaluation once per frame.
_Avoid_: Tick, step

**Run**:
One Brain playing one obstacle sequence from start to death (or time-cap). Produces a Fitness score.
_Avoid_: Trial, attempt, episode

**Generation**:
One round of: all Brains in the Population each complete a Run → Fitness scores computed → parents selected via tournament → crossover → mutation → next Population produced.
_Avoid_: Round, iteration, epoch

**Evolution**:
The complete genetic algorithm process from initial random Population to end-condition (fixed number of Generations or fitness plateau). Produces a lineage of Brains.
_Avoid_: Trial, experiment, simulation

**Session**:
A user's interaction with the software: configure parameters, start an Evolution, watch the Dashboard, replay Brains. A Session may run one or more Evolutions.

### Game World

**Dino**:
The game entity controlled by a Brain. Has position (x, y), velocity (y), and a collision hitbox. Exists in three states: grounded, jumping, and falling.
_Avoid_: Player, character, agent

**Obstacle** (Cactus):
An entity that scrolls from right to left. The Dino must jump over it. Has width, height, and x-position. For v1, only ground-level cacti exist (small and tall sizes).
_Avoid_: Enemy, barrier, block, object

**Game Speed**:
The rate at which the world scrolls (and Obstacles approach). Scales linearly from an initial value to a capped maximum over the course of a Run.
_Avoid_: Scroll speed, difficulty

**Collision**:
When the Dino's hitbox overlaps an Obstacle's hitbox. The Run ends immediately.
_Avoid_: Crash, hit, death-trigger

**Time Cap**:
A configurable maximum duration for a single Run. If exceeded, the Run ends without death. Prevents a Brain that never hits an Obstacle from stalling a Generation.
_Avoid_: Timeout, max duration, cutoff

### Genetic Algorithm

**Brain** (Individual):
The decision-making policy that controls a Dino. Encoded as a fixed-topology neural network. What evolves across Generations.
_Avoid_: Agent, controller, individual, player

**Population**:
The set of all Brains in the current Generation. Fixed size (configurable N). Each Brain in the Population completes a Run during its Generation.
_Avoid_: Pool, generation-set

**Genome**:
A Brain's genetic material — the flattened list of neural network weights and biases. Undergoes Crossover and Mutation.
_Avoid_: Chromosome, DNA, encoding, genotype

**Fitness**:
The score assigned to a Brain after its Run. Determines selection pressure. The fitness function is configurable at Session start (options include: survival distance, obstacle clearance bonus, near-miss bonus, jump-efficiency penalty).

**Elitism**:
The top E brains (configurable fraction of Population) survive unchanged into the next Generation. The remaining slots are filled by offspring.
_Avoid_: Keep-best, survival rate

**Tournament Selection**:
Parent selection mechanism: randomly pick K Brains from the Population, the fittest of the K becomes a parent. Repeat for each offspring needed.
_Avoid_: Competition selection

**Crossover** (Uniform):
Combines two parent Genomes to produce a child Genome. For each weight position, the child inherits from parent A or parent B with equal probability.
_Avoid_: Recombination, breeding

**Mutation** (Gaussian):
Each weight in a child's Genome has probability p of being perturbed by Gaussian noise (mean 0, standard deviation σ). Both p and σ are configurable.
_Avoid_: Perturbation

### Neural Network

**Input**:
The sensory data fed to the Brain each Frame: distance to next Obstacle, an Obstacle-present flag (if no Obstacle is on screen), and game Speed. ~3 values.
_Avoid_: Sensor, perception

**Hidden Layer**:
A single fully-connected layer between Inputs and Output. Size (neuron count) is configurable. Uses ReLU activation.
_Avoid_: Middle layer, dense layer

**Output** (Jump Intensity):
A single continuous value (0–1 via sigmoid) that determines how hard the Dino jumps on the rising edge. 0 = no jump, 1 = full-height jump. Encoded as upward velocity.
_Avoid_: Action, decision, control signal

**Cooldown**:
A minimum number of Frames that must elapse between consecutive jumps. Prevents the Brain from exploiting rapid-fire jumping.
_Avoid_: Jump delay, debounce

**Seed**:
A value that deterministically generates the Obstacle sequence for a Generation. Same Seed within a Generation ensures fair comparisons. A Master Seed (configurable) derives all per-Generation Seeds, making the entire Evolution reproducible.
_Avoid_: Random state, RNG key

### Visualization

**Dashboard**:
The live display during an Evolution. Rendered in a separate matplotlib window. Shows: current Generation number, best Fitness, average Fitness, fitness-over-time chart, and genome statistics for the best Brain.

**Replay**:
A visual playback of the best Brain's Run from a completed Generation, rendered in the main game window. Driven by a JSON Gameplay Log that records per-Frame state (Dino position, Obstacle positions, Brain output). Logs are retained for all Generations during an Evolution and cleaned up at Session end.
