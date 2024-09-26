# sprites.py
import pygame
import random
from settings import *
from utils import get_grid_position
from pathfinding import dfs, bfs, astar, heuristic
# Видаляємо імпорт та створення game_timer з цього файлу

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=pos)

class Dot(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(pos[0]+TILE_SIZE//2, pos[1]+TILE_SIZE//2))

class PowerPellet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(pos[0]+TILE_SIZE//2, pos[1]+TILE_SIZE//2))

class PacManAI(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.original_image = self.image.copy()
        pygame.draw.circle(self.image, YELLOW, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2
        self.lives = 3
        self.score = 0
        self.direction = (0, 0)
        self.path = []
        self.maze = None
        self.powered_up = False
        self.powerup_timer = 0
        self.path_timer = 0

    def update(self, walls, dots, power_pellets, ghosts):
        if self.maze is None:
            return

        self.path_timer += 1
        if self.path_timer >= 15 or not self.path:
            self.path_timer = 0
            self.calculate_new_path(dots, power_pellets, ghosts)

        # Рух по шляху
        if self.path and len(self.path) > 0:
            next_cell = self.path[0]
            target_x = next_cell[0] * TILE_SIZE + TILE_SIZE // 2
            target_y = next_cell[1] * TILE_SIZE + TILE_SIZE // 2
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            dist = (dx**2 + dy**2)**0.5
            if dist != 0:
                move_x = self.speed * dx / dist
                move_y = self.speed * dy / dist
                self.rect.centerx += move_x
                self.rect.centery += move_y

                # Перевірка на досягнення наступної клітинки
                if abs(dx) < self.speed and abs(dy) < self.speed:
                    self.rect.centerx = target_x
                    self.rect.centery = target_y
                    self.path.pop(0)
                    self.update_direction()
        else:
            pass

        # Перевірка стану power-up
        if self.powered_up:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.powered_up = False
                self.image = self.original_image.copy()
                pygame.draw.circle(self.image, YELLOW, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)

    def update_direction(self):
        if self.path and len(self.path) > 0:
            current_pos = (int(self.rect.centerx) // TILE_SIZE, int(self.rect.centery) // TILE_SIZE)
            next_pos = self.path[0]
            self.direction = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
        else:
            self.direction = (0, 0)

    def get_direction(self):
        return self.direction

    def get_grid_position(self):
        return (int(self.rect.centerx) // TILE_SIZE, int(self.rect.centery) // TILE_SIZE)

    def calculate_new_path(self, dots, power_pellets, ghosts):
        start = self.get_grid_position()
        # Знаходимо всі точки та Power Pellets
        dot_positions = [(dot.rect.centerx // TILE_SIZE, dot.rect.centery // TILE_SIZE) for dot in dots]
        pellet_positions = [(pellet.rect.centerx // TILE_SIZE, pellet.rect.centery // TILE_SIZE) for pellet in power_pellets]
        targets = dot_positions + pellet_positions
        if not targets:
            return
        # Вибираємо найкращу ціль з урахуванням ризиків
        min_total_cost = float('inf')
        best_path = []
        for pos in targets:
            path = astar(self.maze, start, pos, self.avoid_ghosts_penalty(ghosts))
            if path:
                total_cost = len(path) + self.estimate_risk(path, ghosts)
                if total_cost < min_total_cost:
                    min_total_cost = total_cost
                    best_path = path
        self.path = best_path
        self.update_direction()

    def estimate_risk(self, path, ghosts):
        risk = 0
        for pos in path:
            for ghost in ghosts:
                ghost_pos = ghost.get_grid_position()
                distance = heuristic(pos, ghost_pos)
                if distance == 0:
                    risk += 1000
                else:
                    risk += max(0, 50 - distance * 5)
        return risk

    def avoid_ghosts_penalty(self, ghosts):
        def penalty(pos):
            penalty = 0
            for ghost in ghosts:
                ghost_pos = ghost.get_grid_position()
                distance = heuristic(pos, ghost_pos)
                if distance == 0:
                    penalty += 1000
                else:
                    penalty += max(0, 50 - distance * 5)
            return penalty
        return penalty

    def notify_maze_changed(self):
        self.path = []
        self.path_timer = 0  # Додано, щоб негайно перерахувати шлях

class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos, color, algorithm, role):
        super().__init__()
        self.base_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.base_image, color, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.initial_position = pos
        self.speed = 4  # Зменшена швидкість для плавного руху
        self.algorithm = algorithm  # 'dfs', 'bfs', 'astar', 'heuristic'
        self.path = []
        self.maze = None
        self.path_timer = 0
        self.needs_new_path = True
        self.frightened_mode = False
        self.target = None  # Ціль для руху в frightened_mode
        self.respawn_timer = 0
        self.state = 'chase'  # Можливі стани: 'chase', 'frightened', 'respawn'
        self.role = role
        self.set_scatter_target()

    def set_scatter_target(self):
        if self.role == 'chaser':
            self.scatter_target = (MAZE_WIDTH - 2, MAZE_HEIGHT - 2)  # Правий нижній кут
        elif self.role == 'ambusher':
            self.scatter_target = (1, 1)  # Лівий верхній кут
        elif self.role == 'patroller':
            self.scatter_target = (MAZE_WIDTH - 2, 1)  # Правий верхній кут
        elif self.role == 'random':
            self.scatter_target = (1, MAZE_HEIGHT - 2)  # Лівий нижній кут
        else:
            self.scatter_target = (MAZE_WIDTH // 2, MAZE_HEIGHT // 2)  # Центр

    def update(self, walls, pacman, ghosts, game_timer):
        if self.maze is None:
            return

        if self.state == 'respawn':
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.state = 'chase'
                self.image = self.base_image.copy()
                self.rect.center = self.initial_position
                self.path = []
                self.needs_new_path = True
            return

        if self.state == 'frightened':
            self.path_timer += 1
            if self.path_timer >= 30 or not self.path:
                self.path_timer = 0
                self.calculate_frightened_path()
            self.follow_path()
            return

        self.path_timer += 1
        if self.path_timer >= 30 or self.needs_new_path:
            self.path_timer = 0
            self.calculate_new_path(pacman, game_timer)

        self.follow_path()

    def follow_path(self):
        # Рухаємось по шляху
        if self.path and len(self.path) > 0:
            next_cell = self.path[0]
            target_x = next_cell[0] * TILE_SIZE + TILE_SIZE // 2
            target_y = next_cell[1] * TILE_SIZE + TILE_SIZE // 2
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            dist = (dx**2 + dy**2)**0.5
            if dist != 0:
                move_x = self.speed * dx / dist
                move_y = self.speed * dy / dist
                self.rect.centerx += move_x
                self.rect.centery += move_y

                # Перевірка на досягнення наступної клітинки
                if abs(dx) < self.speed and abs(dy) < self.speed:
                    self.rect.centerx = target_x
                    self.rect.centery = target_y
                    self.path.pop(0)
        else:
            pass

    def calculate_new_path(self, pacman, game_timer):
        start = self.get_grid_position()
        if self.maze[start[1]][start[0]] == 'X':
            return

        if game_timer.phase == 'chase':
            if self.role == 'chaser':
                goal = pacman.get_grid_position()
            elif self.role == 'ambusher':
                pac_direction = pacman.get_direction()
                goal = (pacman.get_grid_position()[0] + pac_direction[0]*4, pacman.get_grid_position()[1] + pac_direction[1]*4)
                if not self.is_valid_position(goal):
                    goal = pacman.get_grid_position()
            else:
                goal = pacman.get_grid_position()
        elif game_timer.phase == 'scatter':
            goal = self.scatter_target

        self.path = astar(self.maze, start, goal)
        self.needs_new_path = False

    def is_valid_position(self, pos):
        x, y = pos
        return 0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT and self.maze[y][x] != 'X'

    def calculate_frightened_path(self):
        # Вибираємо випадкову точку в лабіринті як ціль
        start = self.get_grid_position()

        # Якщо немає цілі або ціль досягнута, обираємо нову
        if not self.target or start == self.target:
            self.target = self.get_random_target()
        if self.maze[start[1]][start[0]] == 'X' or self.maze[self.target[1]][self.target[0]] == 'X':
            return
        self.path = astar(self.maze, start, self.target)

    def get_random_target(self):
        # Отримуємо всі доступні клітинки
        available_cells = [(x, y) for y in range(MAZE_HEIGHT) for x in range(MAZE_WIDTH) if self.maze[y][x] == '.']
        return random.choice(available_cells)

    def enter_frightened_mode(self):
        self.state = 'frightened'
        self.speed = 0.5  # Зменшуємо швидкість
        self.image = self.base_image.copy()
        pygame.draw.circle(self.image, BLUE, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
        self.path = []
        self.target = self.get_random_target()
        self.needs_new_path = False
        self.path_timer = 0

    def exit_frightened_mode(self):
        self.state = 'chase'
        self.speed = 1
        self.image = self.base_image.copy()
        self.path = []
        self.needs_new_path = True
        self.target = None

    def start_respawn(self):
        self.state = 'respawn'
        self.respawn_timer = 180  # 3 секунди при 60 FPS
        self.rect.center = (MAZE_WIDTH // 2 * TILE_SIZE + TILE_SIZE // 2, MAZE_HEIGHT // 2 * TILE_SIZE + TILE_SIZE // 2)
        self.image = self.base_image.copy()
        pygame.draw.circle(self.image, (128, 128, 128), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
        self.path = []
        self.needs_new_path = False

    def get_grid_position(self):
        return (int(self.rect.centerx) // TILE_SIZE, int(self.rect.centery) // TILE_SIZE)
