# arc_see/runner.py
"""ARC-AGI-3 API integration: play games using the agent."""

import numpy as np
import arc_agi
from arcengine import GameAction, GameState
from arc_see.agent import Agent

# Map string action names to GameAction enum values
_ACTION_MAP = {
    "ACTION1": GameAction.ACTION1,
    "ACTION2": GameAction.ACTION2,
    "ACTION3": GameAction.ACTION3,
    "ACTION4": GameAction.ACTION4,
    "ACTION5": GameAction.ACTION5,
    "ACTION6": GameAction.ACTION6,
    "ACTION7": GameAction.ACTION7,
}
_REVERSE_ACTION_MAP = {v: k for k, v in _ACTION_MAP.items()}


def play_game(
    game_id: str,
    max_turns: int = 500,
    render_mode: str | None = "terminal",
    verbose: bool = True,
) -> dict:
    """Play a single ARC-AGI-3 game using the lens agent."""
    arcade = arc_agi.Arcade()
    env = arcade.make(game_id, render_mode=render_mode)
    if env is None:
        raise RuntimeError(f"Failed to create environment for {game_id}")

    agent = Agent()
    turns = 0
    levels_completed = 0
    lens_usage: dict[tuple[str, str], int] = {}

    # Initial observation
    initial_grid = _extract_grid(env)
    agent.observe(initial_grid)
    agent.perceive()

    for turn in range(max_turns):
        available = [
            _REVERSE_ACTION_MAP[a] for a in env.action_space
            if a in _REVERSE_ACTION_MAP
        ]
        if not available:
            break

        action_name, data = agent.select_action(available)
        game_action = _ACTION_MAP[action_name]

        obs = env.step(game_action, data=data if data else None)
        turns += 1

        if obs is None:
            break

        grid = np.array(obs.frame[-1], dtype=np.int64) if obs.frame else _extract_grid(env)
        agent.observe(grid)
        agent.perceive()
        agent.record(action_name, data)

        # Track lens usage
        top = agent.composer.top_k(agent._annotations, k=3)
        for _, pair in top:
            lens_usage[pair] = lens_usage.get(pair, 0) + 1

        if verbose and turn % 50 == 0:
            conf = agent.graph.confidence(agent._vectorize(agent._annotations))
            print(f"Turn {turn}: graph_size={agent.graph.size}, confidence={conf:.2f}")

        if obs.state == GameState.WIN:
            levels_completed += 1
            if verbose:
                print(f"Level completed at turn {turn}!")
        elif obs.state == GameState.GAME_OVER:
            if verbose:
                print(f"Game over at turn {turn}")
            break

    scorecard = arcade.get_scorecard()
    return {
        "game_id": game_id,
        "turns": turns,
        "levels_completed": levels_completed,
        "graph_size": agent.graph.size,
        "history_length": len(agent.history),
        "top_lens_combinations": sorted(
            lens_usage.items(), key=lambda x: x[1], reverse=True
        )[:10],
        "score": scorecard.score if scorecard else None,
    }


def _extract_grid(env) -> np.ndarray:
    if hasattr(env, 'current_frame'):
        return np.array(env.current_frame, dtype=np.int64)
    return np.zeros((64, 64), dtype=np.int64)


if __name__ == "__main__":
    import sys
    game_id = sys.argv[1] if len(sys.argv) > 1 else "ls20"
    max_turns = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    result = play_game(game_id, max_turns=max_turns)
    print("\n=== Results ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
