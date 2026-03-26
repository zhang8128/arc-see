# arc-see

Perceptual lens system for ARC-AGI-3. The thesis: the bottleneck is seeing, not reasoning.

## Architecture

13 CV lenses compose pairwise. Combinations scored by entropy reduction.
Memory graph records state→action→state transitions using lens annotations.
Action selection blends exploration (lens-guided) and exploitation (graph-guided).

## Testing

```bash
uv run pytest tests/ -q
```

## Key Files

| File | Role |
|------|------|
| `arc_see/lenses/` | 13 primitive lenses: spatial, temporal, structural, relational, goal |
| `arc_see/composer.py` | Pairwise combination scoring via entropy reduction |
| `arc_see/graph.py` | In-game memory graph |
| `arc_see/agent.py` | Core loop: observe → perceive → consult → act |
| `arc_see/runner.py` | ARC-AGI-3 API integration |
