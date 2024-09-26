# pathfinding.py
import random
import heapq
from settings import DIRECTIONS
from utils import heuristic

def dfs(maze, start, goal):
    stack = [(start, [start])]
    visited = set()
    while stack:
        (vertex, path) = stack.pop()
        if vertex == goal:
            return path[1:]  # Повертаємо шлях без початкової позиції
        if vertex not in visited:
            visited.add(vertex)
            neighbors = get_neighbors(maze, vertex)
            random.shuffle(neighbors)
            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    return []

def bfs(maze, start, goal):
    queue = [(start, [start])]
    visited = set()
    visited.add(start)
    while queue:
        (vertex, path) = queue.pop(0)
        if vertex == goal:
            return path[1:]
        for neighbor in get_neighbors(maze, vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []

def astar(maze, start, goal, penalty_func=lambda pos: 0):
    heap = []
    heapq.heappush(heap, (heuristic(start, goal), 0, start, [start]))
    visited = set()
    while heap:
        (est_total, cost_so_far, vertex, path) = heapq.heappop(heap)
        if vertex == goal:
            return path[1:]
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in get_neighbors(maze, vertex):
                if neighbor not in visited:
                    total_cost = cost_so_far + 1 + penalty_func(neighbor)
                    est_total_cost = total_cost + heuristic(neighbor, goal)
                    heapq.heappush(heap, (est_total_cost, total_cost, neighbor, path + [neighbor]))
    return []

def get_neighbors(maze, pos):
    neighbors = []
    for direction in DIRECTIONS:
        x = pos[0] + direction[0]
        y = pos[1] + direction[1]
        if 0 <= x < len(maze[0]) and 0 <= y < len(maze):
            if maze[y][x] != 'X':
                neighbors.append((x, y))
    return neighbors
