# pathfinding.py
import heapq
from settings import GRID_CELL

def heuristic(a, b):
    # Manhattan
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def to_grid(pt):
    x, y = pt
    return int(x) // GRID_CELL, int(y) // GRID_CELL

def to_world(cell):
    gx, gy = cell
    # возвращаем центр клетки
    return gx * GRID_CELL + GRID_CELL // 2, gy * GRID_CELL + GRID_CELL // 2

def astar(grid, start_pos, goal_pos):
    """
    grid: rows x cols, 0=free,1=blocked
    start_pos, goal_pos: world coords (x,y)
    возвращает список мировых точек (waypoints) от start->goal (включая goal)
    """
    cols = len(grid[0])
    rows = len(grid)
    start = to_grid(start_pos)
    goal = to_grid(goal_pos)

    if start == goal:
        return [goal_pos]

    # bounds check
    if not (0 <= start[0] < cols and 0 <= start[1] < rows): return []
    if not (0 <= goal[0] < cols and 0 <= goal[1] < rows): return []

    if grid[start[1]][start[0]] == 1 or grid[goal[1]][goal[0]] == 1:
        return []  # нет пути если ячейки заблокированы

    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    gscore = {start: 0}

    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current == goal:
            # reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            # convert to world coordinates
            waypoints = [to_world(cell) for cell in path]
            return waypoints

        for dx, dy in dirs:
            nb = (current[0] + dx, current[1] + dy)
            if not (0 <= nb[0] < cols and 0 <= nb[1] < rows): continue
            if grid[nb[1]][nb[0]] == 1: continue
            tentative = gscore[current] + 1
            if nb not in gscore or tentative < gscore[nb]:
                gscore[nb] = tentative
                priority = tentative + heuristic(nb, goal)
                heapq.heappush(open_set, (priority, tentative, nb))
                came_from[nb] = current
    return []
