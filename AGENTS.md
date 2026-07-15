## Agent skills

### Issue tracker

Issues live as GitHub issues in `gabrielLoff/genetic-algo-dino-game`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage labels use their default names. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` at root, `docs/adr/` for decisions. See `docs/agents/domain.md`. Read `docs/adr/` before modifying `ga/engine.py` or `nn/network.py` — key design decisions are recorded there.

### Testing

Run tests with:

```bash
python -m pytest tests/ -v
```

Tests live in `tests/` alongside the source modules they exercise. Test files mirror source module names (e.g. `tests/test_dino.py` tests `game/dino.py`).

### Smoke test

Validate the full pipeline runs end-to-end:

```bash
python main.py
```

1. Config screen opens — press Enter to accept defaults
2. Evolution runs, dashboard shows, console prompts between generations
3. Press Enter through generations, Q to quit early
4. Final replay shows the best brain

**Smoke test verification checks:**
- [ ] Config screen renders with parameter descriptions visible on selection
- [ ] Evolution starts and fitness numbers change across generations (not flatlined)
- [ ] After 2-3 generations, best fitness is higher than generation 0
- [ ] Replay shows a dino that interacts with obstacles (even if not perfectly)
- [ ] Dashboard updates each generation (chart lines move)

After any refactor touching `ga/`, `nn/`, `game/dino.py`, or `game/obstacle.py`, run the integration tests:

```bash
python -m pytest tests/test_integration.py -v
```

This validates the GA produces selection pressure (5 gens, 2 fitness functions).

### Gotchas

Recurring bugs and patterns to watch for:

- **Config screen parameter steps** — step size must be range-based (not value-based) and symmetric. Integer steps need a minimum of 1 to avoid being truncated by `int()`.
- **Hitbox coordinate systems** — the Dino uses bottom-aligned y (feet on ground). When passing to `inset_hitbox()`, compute `top = y - height` first. Cactus hitboxes are top-aligned. Mixing coordinate systems silently breaks collision.
- **Stale references after refactors** — when renaming function parameters, search the entire codebase for old variable names. `grep`-and-replace in a single file can miss callers in other modules.
- **Config parameter source-of-truth** — all parameter metadata (default, min, max, label, group) lives in `PARAM_SPECS` in `game/config.py`. Never duplicate defaults across files. The `ConfigMenu` derives its groups from the same spec.
