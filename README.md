# Genetic Algorithm Dino Game

A replica of the Google Chrome Dino Game used to demonstrate neuroevolution in action.
Brains evolve across generations to learn when and how hard to jump over obstacles.

## Quick start

```bash
pip install pygame-ce numpy matplotlib pytest
python main.py
```

1. **Config screen** — adjust GA and game parameters, select presets, or compare two configurations
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

### Presets

8 presets are available in `presets.json`, selectable from the config screen:

| Preset | Purpose |
|--------|---------|
| **Tutorial** | Quick demo (~30s) for first-time presenters |
| Default | Baseline configuration from `config.json` |
| Speedy Evolution | Large population, high mutation — converges fast |
| Precise Timing | Near-miss fitness rewards last-moment jumps |
| Jump Efficiency | Penalizes unnecessary jumps |
| Pure Survival | Raw distance only, no bonuses or penalties |
| Chaos Mode | High mutation, no elitism — wild diversity |
| Elite Guard | High elitism, low mutation — observe stagnation |

### Config screen controls

| Key | Action |
|-----|--------|
| `Tab` | Switch between preset selector and parameters |
| `Left`/`Right` | Cycle presets / adjust parameter values |
| `Up`/`Down` | Navigate parameters |
| `Enter` | Load selected preset / edit parameter value |
| `Space` | Start evolution |
| `Esc` | Quit |
| `C` | Toggle **compare mode** |

### Compare mode

Press `C` on the config screen to compare two presets side by side. Select Preset A and Preset B (`Tab` to switch, `Left`/`Right` to cycle), then press `Space` to run both evolutions in sequence. A comparison table prints to the console showing best fitness, generations, duration, and winner.
