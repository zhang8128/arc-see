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

## First Run Findings (2026-03-26)

0/7 levels on LS20, score 0.0. Agent burned 129 turns without completing a level
(human baseline: 21 actions for level 1). The current memory graph is the wrong
abstraction — it records every transition equally and hits confidence=1.0 after
50 turns despite zero progress. It's "confident" in wrong answers.

What's needed: a **mechanics ledger** (hypothesis-based: "ACTION1 moves cursor up"
with confidence that updates on evidence), **plan memory** (short goal stack: "trying
to move blue block right 3"), and **anti-memory** (what definitively doesn't work,
to avoid wasting actions). These replace the current graph.py, which should be
rethought or replaced entirely.

## Key Files

| File | Role |
|------|------|
| `arc_see/lenses/` | 13 primitive lenses: spatial, temporal, structural, relational, goal |
| `arc_see/composer.py` | Pairwise combination scoring via entropy reduction |
| `arc_see/graph.py` | In-game memory graph |
| `arc_see/agent.py` | Core loop: observe → perceive → consult → act |
| `arc_see/runner.py` | ARC-AGI-3 API integration |
