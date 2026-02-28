import random
import pygame
import torch

from dqn_agent import EnemyDQN
from game_core import Game, GRID_WIDTH, GRID_HEIGHT


def build_state(game):
    ex = game.enemy.grid_x
    ey = game.enemy.grid_y
    px = game.player.grid_x
    py = game.player.grid_y
    dx = (px - ex) / GRID_WIDTH
    dy = (py - ey) / GRID_HEIGHT
    dist = (abs(px - ex) + abs(py - ey)) / (GRID_WIDTH + GRID_HEIGHT)
    up_block = 1.0 if ey - 1 < 0 or (ex, ey - 1) in game.walls else 0.0
    down_block = 1.0 if ey + 1 >= GRID_HEIGHT or (ex, ey + 1) in game.walls else 0.0
    left_block = 1.0 if ex - 1 < 0 or (ex - 1, ey) in game.walls else 0.0
    right_block = 1.0 if ex + 1 >= GRID_WIDTH or (ex + 1, ey) in game.walls else 0.0
    px_norm = px / GRID_WIDTH
    py_norm = py / GRID_HEIGHT
    ex_norm = ex / GRID_WIDTH
    ey_norm = ey / GRID_HEIGHT
    return [
        dx,
        dy,
        dist,
        up_block,
        down_block,
        left_block,
        right_block,
        px_norm,
        py_norm,
        ex_norm,
        ey_norm,
    ]


def make_enemy_controller(model_path="enemy_dqn.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_dim = 11
    action_dim = 4
    model = EnemyDQN(input_dim, action_dim).to(device)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    def controller(game):
        state = build_state(game)
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        with torch.no_grad():
            q_values = model(s)
            dqn_action = int(torch.argmax(q_values, dim=1).item())
        rule_action = game.enemy.chase_player_action(game.player)
        if random.random() < 0.5:
            return rule_action
        return dqn_action

    return controller


if __name__ == "__main__":
    pygame.init()
    controller = make_enemy_controller()
    game = Game(enemy_controller=controller)
    game.run()
