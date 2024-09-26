# settings.py
import pygame

# Екран
TILE_SIZE = 20
MAZE_WIDTH = 27  # Непарне число для генерації лабіринту
MAZE_HEIGHT = 31
SCREEN_WIDTH = MAZE_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAZE_HEIGHT * TILE_SIZE

# Кольори
BLACK = (0, 0, 0)
BLUE = (0, 0, 155)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)

# Напрямки
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# FPS
FPS = 60

# Шрифти
pygame.font.init()
FONT_SMALL = pygame.font.SysFont('Arial', 24)
FONT_MEDIUM = pygame.font.SysFont('Arial', 32)
FONT_LARGE = pygame.font.SysFont('Arial', 48)
