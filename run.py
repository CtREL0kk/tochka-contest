import sys
import heapq
from typing import List, Tuple


def solve(lines: List[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    start_state, depth = parse_maze(lines)
    return find_min_energy(start_state, depth)


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


def parse_maze(lines: List[str]) -> Tuple[Tuple, int]:
    depth = len(lines) - 3
    hallway = tuple(lines[1][1:12])
    rooms: List[List[str]] = [[""] * depth for _ in range(4)]

    for d in range(depth):
        row = lines[2 + d]
        for r in range(4):
            rooms[r][d] = row[3 + 2 * r]

    rooms_t = tuple(tuple(room) for room in rooms)
    start_state = (hallway, rooms_t)
    return start_state, depth


def build_target(depth: int) -> Tuple:
    hallway = tuple('.' for _ in range(11))
    rooms = []
    for r in range(4):
        rooms.append(tuple(chr(ord('A') + r) for _ in range(depth)))
    return hallway, tuple(rooms)

def generate_moves(state: Tuple) -> List[Tuple[Tuple, int]]:
    room_pos = (2, 4, 6, 8)
    free_space_pos = (0, 1, 3, 5, 7, 9, 10)
    step_cost = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
    hallway, rooms = state
    moves = []

    depth = len(rooms[0])

    for pos, c in enumerate(hallway):
        if c == '.':
            continue

        room_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}[c]
        room = rooms[room_idx]
        door_pos_idx = room_pos[room_idx]

        if any(cell != '.' and cell != c for cell in room):
            continue

        step = 1 if door_pos_idx > pos else -1
        blocked = False
        for current_hallway_pos in range(pos + step, door_pos_idx + step, step):
            if hallway[current_hallway_pos] != '.':
                blocked = True
                break
        if blocked:
            continue

        depth_idx = None
        for d in range(depth - 1, -1, -1):
            if room[d] == '.':
                depth_idx = d
                break

        steps = abs(door_pos_idx - pos) + (depth_idx + 1)
        cost = steps * step_cost[c]

        new_hallway = list(hallway)
        new_hallway[pos] = '.'

        new_rooms = [list(r) for r in rooms]
        new_rooms[room_idx][depth_idx] = c

        new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))
        moves.append((new_state, cost))

    for room_idx, room in enumerate(rooms):
        room_type = chr(ord('A') + room_idx)

        if all(cell == '.' or cell == room_type for cell in room):
            continue

        depth_idx = None
        nearest_cell_to_move = None
        for d, cell in enumerate(room):
            if cell == '.':
                continue
            depth_idx = d
            nearest_cell_to_move = cell
            break

        door_pos_idx = room_pos[room_idx]

        current_hallway_pos = door_pos_idx
        while True:
            current_hallway_pos -= 1
            if current_hallway_pos < 0 or hallway[current_hallway_pos] != '.':
                break
            if current_hallway_pos in free_space_pos:
                steps = door_pos_idx - current_hallway_pos + (depth_idx + 1)
                cost = steps * step_cost[nearest_cell_to_move]

                new_hallway = list(hallway)
                new_hallway[current_hallway_pos] = nearest_cell_to_move

                new_rooms = [list(r) for r in rooms]
                new_rooms[room_idx][depth_idx] = '.'

                new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))
                moves.append((new_state, cost))

        current_hallway_pos = door_pos_idx
        while True:
            current_hallway_pos += 1
            if current_hallway_pos >= len(hallway) or hallway[current_hallway_pos] != '.':
                break
            if current_hallway_pos in free_space_pos:
                steps = current_hallway_pos - door_pos_idx + (depth_idx + 1)
                cost = steps * step_cost[nearest_cell_to_move]

                new_hallway = list(hallway)
                new_hallway[current_hallway_pos] = nearest_cell_to_move

                new_rooms = [list(r) for r in rooms]
                new_rooms[room_idx][depth_idx] = '.'

                new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))
                moves.append((new_state, cost))

    return moves


def find_min_energy(start_state: Tuple, depth: int) -> int:
    target_state = build_target(depth)
    best = {start_state: 0}
    heap = [(0, start_state)]

    while heap:
        cost, state = heapq.heappop(heap)
        if cost != best.get(state, 10 ** 18):
            continue

        if state == target_state:
            return cost

        for next_state, move_cost in generate_moves(state):
            new_cost = cost + move_cost
            if new_cost < best.get(next_state, 10 ** 18):
                best[next_state] = new_cost
                heapq.heappush(heap, (new_cost, next_state))

    return -1


if __name__ == "__main__":
    main()
