import math
import random

from game_core import GRID_WIDTH, GRID_HEIGHT, generate_walls, Player, Enemy


class RLEnvironment:
    def __init__(self, max_steps=400):
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.walls = generate_walls()
        self.player = Player(3, GRID_HEIGHT // 2)
        self.enemy = Enemy(GRID_WIDTH - 4, GRID_HEIGHT // 2)
        self.player.walls = self.walls
        self.enemy.walls = self.walls
        self.steps = 0
        self.done = False
        return self.get_state()

    def scripted_player_step(self):
        dx = 0
        dy = 0
        diff_x = self.enemy.grid_x - self.player.grid_x
        diff_y = self.enemy.grid_y - self.player.grid_y
        if random.random() < 0.6:
            if abs(diff_x) > abs(diff_y):
                if diff_x > 0:
                    dx = -1
                elif diff_x < 0:
                    dx = 1
            else:
                if diff_y > 0:
                    dy = -1
                elif diff_y < 0:
                    dy = 1
        else:
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
            dx, dy = direction
        self.player.move(dx, dy)

    def get_state(self):
        ex = self.enemy.grid_x
        ey = self.enemy.grid_y
        px = self.player.grid_x
        py = self.player.grid_y
        dx = (px - ex) / GRID_WIDTH
        dy = (py - ey) / GRID_HEIGHT
        dist = (abs(px - ex) + abs(py - ey)) / (GRID_WIDTH + GRID_HEIGHT)
        up_block = 1.0 if ey - 1 < 0 or (ex, ey - 1) in self.walls else 0.0
        down_block = 1.0 if ey + 1 >= GRID_HEIGHT or (ex, ey + 1) in self.walls else 0.0
        left_block = 1.0 if ex - 1 < 0 or (ex - 1, ey) in self.walls else 0.0
        right_block = 1.0 if ex + 1 >= GRID_WIDTH or (ex + 1, ey) in self.walls else 0.0
        px_norm = px / GRID_WIDTH
        py_norm = py / GRID_HEIGHT
        ex_norm = ex / GRID_WIDTH
        ey_norm = ey / GRID_HEIGHT
        state = [
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
        return state

    def step(self, action):
        if self.done:
            return self.get_state(), 0.0, True
        self.steps += 1
        ex = self.enemy.grid_x
        ey = self.enemy.grid_y
        px = self.player.grid_x
        py = self.player.grid_y
        dist_before = abs(px - ex) + abs(py - ey)
        self.enemy.step(action)
        self.scripted_player_step()
        ex = self.enemy.grid_x
        ey = self.enemy.grid_y
        px = self.player.grid_x
        py = self.player.grid_y
        dist_after = abs(px - ex) + abs(py - ey)
        reward = 0.0
        if dist_after < dist_before:
            reward += 0.1
        else:
            reward -= 0.1
        if dist_after <= 3:
            reward += 0.05
        reward -= 0.01
        if ex == px and ey == py:
            reward += 10.0
            self.done = True
        if self.steps >= self.max_steps and not self.done:
            reward -= 5.0
            self.done = True
        return self.get_state(), reward, self.done
