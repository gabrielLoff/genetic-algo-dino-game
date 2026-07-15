# Genetic Algorithm Dino Game

A replica of the Google Chrome Dino Game used to demonstrate neuroevolution in action.
Brains evolve across generations to learn when and how hard to jump over obstacles.

## Quick start

```bash
pip install pygame-ce numpy matplotlib pytest
python main.py
```

1. **Config screen** — adjust GA and game parameters (arrows + left/right, Enter to start)
2. **Evolution** — runs headless with a live matplotlib dashboard showing fitness progress
3. **Replay** — the best brain from the entire evolution plays back in the game window

## What it does

- A population of neural-network "brains" controls a dino in a side-scrolling obstacle course
- Each brain's genome encodes the weights of a 3→H→1 feedforward NN
- Brains compete: survive longest → highest fitness → selected to breed
- Tournament selection, uniform crossover, and Gaussian mutation produce each new generation
- Configurable fitness functions: survival distance, obstacle clearance bonus, near-miss reward, jump efficiency penalty

## Running tests

```bash
pytest tests/
```

## Configuration

Edit `config.json` to override defaults, or use the in-game config screen on startup.
