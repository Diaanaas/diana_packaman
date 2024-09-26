# utils.py
import pygame
from settings import TILE_SIZE

def load_image(path, scale=None):
    image = pygame.image.load(path).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image

def get_grid_position(pos):
    x, y = pos
    return x // TILE_SIZE, y // TILE_SIZE

def heuristic(a, b):
    # Манхеттенська відстань
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
