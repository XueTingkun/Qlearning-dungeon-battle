# Q-learning Dungeon Battle

A small 2D top-down game where a human player fights against an AI-controlled enemy in a dungeon room.
The enemy movement policy is trained using Deep Q-learning (DQN).

## Game overview

- Grid-based map (28×18) with simple cross-shaped walls.
- Player:
  - Move: `W`, `A`, `S`, `D`
  - Aim: arrow keys
  - Shoot: `SPACE`
  - 3 HP, turns lighter when taking damage
- Enemy:
  - 3 HP, turns yellow when taking damage
  - Trained with a DQN and combined with a rule-based chase policy in the final demo
- Press `ENTER` to start, `R` to restart, `ESC` to quit.

## Files

- `game_core.py` – Pygame game logic, UI, HP system and effects.
- `rl_env.py` – RL environment for training the enemy.
- `dqn_agent.py` – DQN implementation and training loop (PyTorch).
- `play_with_ai.py` – Human vs trained AI mode (hybrid control).
- `A1_Report.docx` – Project report.

## How to run

1. Install dependencies:

   ```bash
   pip install pygame torch
