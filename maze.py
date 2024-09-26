# maze.py
import random

import pygame

from settings import MAZE_WIDTH, MAZE_HEIGHT, DIRECTIONS

def generate_maze(level):
    maze = [['X'] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
    walls_list = []
    start_x = MAZE_WIDTH // 2
    start_y = MAZE_HEIGHT // 2
    maze[start_y][start_x] = '.'

    walls_list.extend([(start_x + dx, start_y + dy, start_x + 2*dx, start_y + 2*dy) for dx, dy in DIRECTIONS])

    while walls_list:
        (wx, wy, nx, ny) = walls_list.pop(random.randint(0, len(walls_list) - 1))
        if 0 < nx < MAZE_WIDTH and 0 < ny < MAZE_HEIGHT:
            if maze[ny][nx] == 'X':
                maze[wy][wx] = '.'
                maze[ny][nx] = '.'
                for dx, dy in DIRECTIONS:
                    walls_list.append((nx + dx, ny + dy, nx + 2*dx, ny + 2*dy))

    # Додаємо додаткові з'єднання для створення циклів
    for _ in range(level * 10):
        x = random.randrange(1, MAZE_WIDTH - 1, 2)
        y = random.randrange(1, MAZE_HEIGHT - 1, 2)
        if maze[y][x] == '.':
            direction = random.choice(DIRECTIONS)
            nx, ny = x + direction[0], y + direction[1]
            if 0 < nx < MAZE_WIDTH - 1 and 0 < ny < MAZE_HEIGHT - 1:
                if maze[ny][nx] == 'X':
                    maze[ny][nx] = '.'

    # Гарантуємо, що стартові позиції вільні
    positions = [
        (MAZE_WIDTH // 2, MAZE_HEIGHT // 2),  # Pac-Man
        (1, 1),  # Ghost 1
        (MAZE_WIDTH - 2, 1),  # Ghost 2
        (1, MAZE_HEIGHT - 2),  # Ghost 3
        (MAZE_WIDTH - 2, MAZE_HEIGHT - 2)  # Ghost 4
    ]
    for x, y in positions:
        maze[y][x] = '.'

    return maze

def is_maze_valid(maze, positions):
    from pathfinding import bfs
    for pos in positions[1:]:
        path = bfs(maze, positions[0], pos)
        if not path:
            return False
    return True

def create_level(maze, all_sprites, dots, power_pellets):
    from sprites import Wall, Dot, PowerPellet
    from settings import TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT
    walls = pygame.sprite.Group()
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            if tile == 'X':
                wall = Wall(pos)
                walls.add(wall)
                all_sprites.add(wall)
            elif tile == '.':
                dot = Dot(pos)
                dots.add(dot)
                all_sprites.add(dot)
    # Додаємо Power Pellets
    pellet_positions = [(1, 1), (MAZE_WIDTH - 2, 1), (1, MAZE_HEIGHT - 2), (MAZE_WIDTH - 2, MAZE_HEIGHT - 2)]
    for x, y in pellet_positions:
        pellet = PowerPellet((x * TILE_SIZE, y * TILE_SIZE))
        power_pellets.add(pellet)
        all_sprites.add(pellet)
    return walls
