import time

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def find_nearest_cell(current_pos, unvisited_cells):
    min_dist = float("inf")
    nearest_cell = None
    for cell in unvisited_cells:
        dist = manhattan_distance(current_pos, cell)
        if dist < min_dist:
            min_dist = dist
            nearest_cell = cell
    return nearest_cell


def find_shortest_path(matrix):
    non_zero_cells = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] != 0:
                non_zero_cells.append((i, j))

    current_pos = non_zero_cells[0]
    path = [current_pos]
    non_zero_cells.remove(current_pos)

    while non_zero_cells:
        nearest_cell = find_nearest_cell(current_pos, non_zero_cells)
        path.append(nearest_cell)
        non_zero_cells.remove(nearest_cell)
        current_pos = nearest_cell

    return path


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_x != 0:
        delta_y = 0
    return (delta_x, delta_y)


def complete_path(start_x, start_y, dest_x, dest_y):
    current_x, current_y = start_x, start_y
    path = [(current_x, current_y)]

    while (current_x, current_y) != (dest_x, dest_y):
        direction = get_direction(current_x, current_y, dest_x, dest_y)
        current_x += direction[0]
        current_y += direction[1]
        path.append((current_x, current_y))

    return path


# Example matrix
matrix = [
    [1, 0, 3, 0, 0, 0, 0],
    [0, 2, 4, 0, 0, 0, 0],
    [0, 4, 6, 0, 0, 0, 0],
    [0, 2, 4, 0, 1, 1, 0],
    [1, 0, 6, 0, 0, 0, 0],
]

start = time.time()
shortest_path = find_shortest_path(matrix)
print(shortest_path)

arr_tot = [(0, 0)]
for i in range(len(shortest_path) - 1):
    temp = complete_path(
        shortest_path[i][0],
        shortest_path[i][1],
        shortest_path[i + 1][0],
        shortest_path[i + 1][1],
    )
    for j in range(1, len(temp)):
        arr_tot.append(temp[j])

end = time.time()
print(arr_tot)
print(f"time = {(end - start) * 1000} ms")
