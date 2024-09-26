# main.py
import pygame
import sys
import random
from settings import *
from sprites import PacManAI, Ghost
from maze import generate_maze, is_maze_valid, create_level
from game_timer import GameTimer

# Створення екземпляра GameTimer
game_timer = GameTimer()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man AI")
    clock = pygame.time.Clock()

    # Ініціалізація груп спрайтів
    all_sprites = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()
    dots = pygame.sprite.Group()
    power_pellets = pygame.sprite.Group()

    # Створення Pac-Man та привидів
    pacman = PacManAI((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    ghost1 = Ghost((TILE_SIZE + TILE_SIZE // 2, TILE_SIZE + TILE_SIZE // 2), RED, 'dfs', role='chaser')
    ghost2 = Ghost((SCREEN_WIDTH - TILE_SIZE - TILE_SIZE // 2, TILE_SIZE + TILE_SIZE // 2), PINK, 'bfs', role='ambusher')

    ghosts.add(ghost1, ghost2)
    all_sprites.add(pacman)
    all_sprites.add(ghosts)

    current_level = 1
    max_levels = 5  # Кількість рівнів з наростанням складності

    running = True
    while running:
        # Генерація лабіринту з перевіркою зв'язності
        valid_maze = False
        while not valid_maze:
            maze = generate_maze(current_level)
            positions = [
                (MAZE_WIDTH // 2, MAZE_HEIGHT // 2),  # Pac-Man
                (1, 1),  # Ghost 1
                (MAZE_WIDTH - 2, 1),  # Ghost 2
            ]
            valid_maze = is_maze_valid(maze, positions)
        walls = create_level(maze, all_sprites, dots, power_pellets)
        pacman.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pacman.direction = (0, 0)
        pacman.powered_up = False
        pacman.powerup_timer = 0
        pacman.image = pacman.original_image.copy()
        pygame.draw.circle(pacman.image, YELLOW, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
        pacman.maze = maze
        pacman.path = []

        for ghost in ghosts:
            # Встановлюємо початкові позиції привидів
            if ghost.algorithm == 'dfs':
                ghost.rect.center = (TILE_SIZE + TILE_SIZE // 2, TILE_SIZE + TILE_SIZE // 2)
            elif ghost.algorithm == 'bfs':
                ghost.rect.center = (SCREEN_WIDTH - TILE_SIZE - TILE_SIZE // 2, TILE_SIZE + TILE_SIZE // 2)
            ghost.initial_position = ghost.rect.center
            ghost.maze = maze
            ghost.path = []
            ghost.path_timer = 0
            ghost.needs_new_path = True
            ghost.frightened_mode = False
            ghost.speed = 1  # Збільшена швидкість
            ghost.image = ghost.base_image.copy()
            ghost.target = None
            ghost.state = 'chase'

        level_running = True
        while level_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    level_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        # Перехід на наступний рівень при натисканні 'N'
                        current_level += 1
                        if current_level <= max_levels:
                            print("Перехід на рівень", current_level)
                        else:
                            print("Ви досягли максимального рівня!")
                            current_level = 1  # Починаємо знову
                        level_running = False

            pacman.update(walls, dots, power_pellets, ghosts)

            for ghost in ghosts:
                ghost.update(walls, pacman, ghosts, game_timer)

            game_timer.update()

            # Перевірка зіткнення Pac-Man з точками
            eaten_dots = pygame.sprite.spritecollide(pacman, dots, True)
            pacman.score += len(eaten_dots) * 10  # Кожна точка дає 10 балів
            if eaten_dots:
                pacman.notify_maze_changed()

            # Перевірка зіткнення з Power Pellets
            eaten_pellets = pygame.sprite.spritecollide(pacman, power_pellets, True)
            if eaten_pellets:
                pacman.powered_up = True
                pacman.powerup_timer = 600  # 10 секунд при 60 FPS
                pacman.image.fill((0, 0, 0, 0))
                pygame.draw.circle(pacman.image, (255, 215, 0), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
                for ghost in ghosts:
                    if ghost.state != 'respawn':
                        ghost.enter_frightened_mode()

            # Перевірка на зіткнення з привидами
            collided_ghost = pygame.sprite.spritecollideany(pacman, ghosts)
            if collided_ghost and collided_ghost.state != 'respawn':
                if pacman.powered_up and collided_ghost.state == 'frightened':
                    # Pac-Man їсть привида
                    collided_ghost.start_respawn()
                    pacman.score += 200
                elif collided_ghost.state != 'frightened':
                    # Pac-Man втрачає життя
                    pacman.lives -= 1
                    if pacman.lives <= 0:
                        print("Гру закінчено!")
                        running = False
                        level_running = False
                    else:
                        # Перезапуск позиції Pac-Man
                        pacman.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                        pacman.direction = (0, 0)
                        pacman.path = []
                        # Перезапуск привидів
                        for ghost in ghosts:
                            ghost.rect.center = ghost.initial_position
                            ghost.path = []
                            ghost.path_timer = 0
                            ghost.needs_new_path = True
                            ghost.state = 'chase'
                            ghost.image = ghost.base_image.copy()
                            ghost.speed = 10  # Збільшена швидкість

            # Перевірка на завершення рівня
            if len(dots) == 0:
                current_level += 1
                if current_level <= max_levels:
                    print("Рівень пройдено!")
                    level_running = False
                else:
                    print("Ви виграли гру!")
                    running = False
                    level_running = False

            # Малювання
            screen.fill(BLACK)
            all_sprites.draw(screen)

            # Прибрано відображення рахунку та життів

            pygame.display.flip()
            clock.tick(FPS)

        # Очищення спрайтів для наступного рівня
        walls.empty()
        dots.empty()
        power_pellets.empty()
        all_sprites.empty()
        all_sprites.add(pacman)
        all_sprites.add(ghosts)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
