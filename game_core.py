import pygame
import sys


GRID_SIZE = 32
GRID_WIDTH = 28
GRID_HEIGHT = 18
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
PLAYER_COLOR = (50, 200, 50)
ENEMY_COLOR = (80, 160, 255)
BULLET_COLOR = (255, 255, 0)
BG_COLOR = (20, 20, 20)
WALL_COLOR = (100, 100, 100)


def generate_walls():
    walls = set()
    y_mid = GRID_HEIGHT // 2
    for x in range(3, GRID_WIDTH - 3):
        if x < GRID_WIDTH // 2 - 3 or x > GRID_WIDTH // 2 + 3:
            walls.add((x, y_mid))
    for y in range(3, GRID_HEIGHT - 3):
        if y < y_mid - 2 or y > y_mid + 2:
            walls.add((3, y))
            walls.add((GRID_WIDTH - 4, y))
    return walls


class Player:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.dir_x = 0
        self.dir_y = -1
        self.speed = 1
        self.walls = set()
        self.max_hp = 3
        self.hp = 3
        self.hurt_timer = 0

    def handle_input(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx = -1
            dy = 0
        elif keys[pygame.K_d]:
            dx = 1
            dy = 0
        elif keys[pygame.K_w]:
            dx = 0
            dy = -1
        elif keys[pygame.K_s]:
            dx = 0
            dy = 1
        aim_dx = 0
        aim_dy = 0
        if keys[pygame.K_LEFT]:
            aim_dx = -1
            aim_dy = 0
        elif keys[pygame.K_RIGHT]:
            aim_dx = 1
            aim_dy = 0
        elif keys[pygame.K_UP]:
            aim_dx = 0
            aim_dy = -1
        elif keys[pygame.K_DOWN]:
            aim_dx = 0
            aim_dy = 1
        if aim_dx != 0 or aim_dy != 0:
            self.dir_x = aim_dx
            self.dir_y = aim_dy
        if dx != 0 or dy != 0:
            self.move(dx, dy)

    def move(self, dx, dy):
        new_x = self.grid_x + dx * self.speed
        new_y = self.grid_y + dy * self.speed
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and (new_x, new_y) not in self.walls:
            self.grid_x = new_x
            self.grid_y = new_y

    def shoot(self):
        return Bullet(self.grid_x, self.grid_y, self.dir_x, self.dir_y, owner="player")

    def draw(self, surface):
        rect = pygame.Rect(self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        color = PLAYER_COLOR
        if self.hurt_timer > 0:
            color = (255, 120, 120)
        pygame.draw.rect(surface, color, rect)
        cx = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        cy = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        if self.dir_x == 0 and self.dir_y == -1:
            points = [(cx, cy - GRID_SIZE // 2 + 4), (cx - 6, cy - 2), (cx + 6, cy - 2)]
        elif self.dir_x == 0 and self.dir_y == 1:
            points = [(cx, cy + GRID_SIZE // 2 - 4), (cx - 6, cy + 2), (cx + 6, cy + 2)]
        elif self.dir_x == -1 and self.dir_y == 0:
            points = [(cx - GRID_SIZE // 2 + 4, cy), (cx - 2, cy - 6), (cx - 2, cy + 6)]
        else:
            points = [(cx + GRID_SIZE // 2 - 4, cy), (cx + 2, cy - 6), (cx + 2, cy + 6)]
        pygame.draw.polygon(surface, BULLET_COLOR, points)


class Enemy:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.speed = 1
        self.walls = set()
        self.max_hp = 3
        self.hp = 3
        self.hurt_timer = 0

    def step(self, action):
        if action == 0:
            dx, dy = 0, -1
        elif action == 1:
            dx, dy = 0, 1
        elif action == 2:
            dx, dy = -1, 0
        else:
            dx, dy = 1, 0
        self.move(dx, dy)

    def move(self, dx, dy):
        new_x = self.grid_x + dx * self.speed
        new_y = self.grid_y + dy * self.speed
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and (new_x, new_y) not in self.walls:
            self.grid_x = new_x
            self.grid_y = new_y

    def chase_player_action(self, player):
        dx = 0
        dy = 0
        if abs(player.grid_x - self.grid_x) > abs(player.grid_y - self.grid_y):
            if player.grid_x > self.grid_x:
                dx = 1
            elif player.grid_x < self.grid_x:
                dx = -1
        else:
            if player.grid_y > self.grid_y:
                dy = 1
            elif player.grid_y < self.grid_y:
                dy = -1
        if dx == 0 and dy == 0:
            return 0
        if dx == 0 and dy == -1:
            return 0
        if dx == 0 and dy == 1:
            return 1
        if dx == -1 and dy == 0:
            return 2
        return 3

    def draw(self, surface):
        rect = pygame.Rect(self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        color = ENEMY_COLOR
        if self.hurt_timer > 0:
            color = (255, 255, 120)
        pygame.draw.rect(surface, color, rect)


class Bullet:
    def __init__(self, grid_x, grid_y, dir_x, dir_y, owner):
        self.x = grid_x + 0.5
        self.y = grid_y + 0.5
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = 0.4
        self.owner = owner
        self.alive = True

    def update(self):
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        if self.x < 0 or self.x >= GRID_WIDTH or self.y < 0 or self.y >= GRID_HEIGHT:
            self.alive = False

    def grid_position(self):
        return int(self.x), int(self.y)

    def draw(self, surface):
        rect = pygame.Rect(int(self.x * GRID_SIZE - GRID_SIZE / 4), int(self.y * GRID_SIZE - GRID_SIZE / 4), GRID_SIZE // 2, GRID_SIZE // 2)
        pygame.draw.rect(surface, BULLET_COLOR, rect)


class Game:
    def __init__(self, enemy_controller=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Player vs Q-learning Enemy (Base Game)")
        self.clock = pygame.time.Clock()
        self.reset()
        self.enemy_step_counter = 0
        self.enemy_controller = enemy_controller
        self.state = "menu"

    def reset(self):
        self.walls = generate_walls()
        self.player = Player(3, GRID_HEIGHT // 2)
        self.enemy = Enemy(GRID_WIDTH - 4, GRID_HEIGHT // 2)
        self.walls.discard((self.player.grid_x, self.player.grid_y))
        self.walls.discard((self.enemy.grid_x, self.enemy.grid_y))
        self.player.walls = self.walls
        self.enemy.walls = self.walls
        self.player.hp = self.player.max_hp
        self.enemy.hp = self.enemy.max_hp
        self.player.hurt_timer = 0
        self.enemy.hurt_timer = 0
        self.bullets = []
        self.running = True
        self.game_over = False
        self.win_text = ""

    def spawn_player_bullet(self):
        bullet = self.player.shoot()
        self.bullets.append(bullet)

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        if self.player.hurt_timer > 0:
            self.player.hurt_timer -= 1
        if self.enemy.hurt_timer > 0:
            self.enemy.hurt_timer -= 1
        self.enemy_step_counter += 1
        if self.enemy_step_counter >= 2:
            self.enemy_step_counter = 0
            if self.enemy_controller is not None:
                enemy_action = self.enemy_controller(self)
            else:
                enemy_action = self.enemy.chase_player_action(self.player)
            self.enemy.step(enemy_action)
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.alive]
        self.handle_collisions()

    def handle_collisions(self):
        for bullet in self.bullets:
            if bullet.owner == "player":
                bx, by = bullet.grid_position()
                if bx == self.enemy.grid_x and by == self.enemy.grid_y:
                    if self.enemy.hurt_timer == 0:
                        self.enemy.hp -= 1
                        self.enemy.hurt_timer = 12
                        if self.enemy.hp <= 0:
                            self.game_over = True
                            self.win_text = "Player Wins"
                    bullet.alive = False
                if (bx, by) in self.walls:
                    bullet.alive = False
        if self.player.grid_x == self.enemy.grid_x and self.player.grid_y == self.enemy.grid_y:
            if self.player.hurt_timer == 0 and not self.game_over:
                self.player.hp -= 1
                self.player.hurt_timer = 12
                if self.player.hp <= 0:
                    self.game_over = True
                    self.win_text = "Enemy Wins"

    def draw(self):
        self.screen.fill(BG_COLOR)
        if self.state == "menu":
            font_title = pygame.font.SysFont(None, 64)
            font_text = pygame.font.SysFont(None, 32)
            title = font_title.render("Q-learning Dungeon Battle", True, (255, 255, 255))
            rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(title, rect)
            lines = [
                "Move: WASD, Aim: Arrow keys, Shoot: SPACE",
                "Both player and enemy have 3 HP",
                "Press ENTER to start, R to restart, ESC to quit",
            ]
            for i, line in enumerate(lines):
                text = font_text.render(line, True, (220, 220, 220))
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60 + i * 30))
                self.screen.blit(text, rect)
            pygame.display.flip()
            return
        for x in range(GRID_WIDTH):
            pygame.draw.line(self.screen, (40, 40, 40), (x * GRID_SIZE, 0), (x * GRID_SIZE, SCREEN_HEIGHT))
        for y in range(GRID_HEIGHT):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y * GRID_SIZE), (SCREEN_WIDTH, y * GRID_SIZE))
        for wx, wy in self.walls:
            rect = pygame.Rect(wx * GRID_SIZE, wy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, WALL_COLOR, rect)
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        font_ui = pygame.font.SysFont(None, 28)
        hp_text_p = font_ui.render(f"Player HP: {self.player.hp}/3", True, (255, 255, 255))
        self.screen.blit(hp_text_p, (10, 8))
        hp_text_e = font_ui.render(f"Enemy HP: {self.enemy.hp}/3", True, (255, 255, 255))
        rect_e = hp_text_e.get_rect(topright=(SCREEN_WIDTH - 10, 8))
        self.screen.blit(hp_text_e, rect_e)
        if self.game_over:
            font = pygame.font.SysFont(None, 48)
            text = font.render(self.win_text + " - Press R to restart", True, (255, 255, 255))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, rect)
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_RETURN and self.state == "menu":
                        self.reset()
                        self.state = "playing"
                    if event.key == pygame.K_SPACE and not self.game_over:
                        self.spawn_player_bullet()
                    if event.key == pygame.K_r:
                        self.reset()
                        self.state = "playing"
            if self.state == "playing" and not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(10)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()

