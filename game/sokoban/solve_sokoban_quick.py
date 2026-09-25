import random
from collections import deque


def solve_sokoban_quick(width, height, walls, targets, initial_boxes, start_player):
    """생성된 맵이 실제 클리어 가능한지 초고속으로 검증하는 함수"""
    corner_deadlocks = set()
    for y in range(height):
        for x in range(width):
            if (x, y) in walls or (x, y) in targets:
                continue
            up = (x, y - 1) in walls or y - 1 < 0
            down = (x, y + 1) in walls or y + 1 >= height
            left = (x - 1, y) in walls or x - 1 < 0
            right = (x + 1, y) in walls or x + 1 >= width
            if (up and left) or (up and right) or (down and left) or (down and right):
                corner_deadlocks.add((x, y))

    start_state = (start_player, initial_boxes)
    queue = deque([start_state])
    visited = {start_state}
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while queue:
        curr_player, current_boxes = queue.popleft()
        if current_boxes == targets:
            return True  # 클리어 성공 가능한 맵

        p_x, p_y = curr_player
        for dx, dy in directions:
            next_p = (p_x + dx, p_y + dy)
            if (
                next_p in walls
                or next_p[0] < 0
                or next_p[0] >= width
                or next_p[1] < 0
                or next_p[1] >= height
            ):
                continue
            if next_p in current_boxes:
                next_box = (next_p[0] + dx, next_p[1] + dy)
                if (
                    next_box in walls
                    or next_box in current_boxes
                    or next_box[0] < 0
                    or next_box[0] >= width
                    or next_box[1] < 0
                    or next_box[1] >= height
                ):
                    continue
                if next_box in corner_deadlocks:
                    continue
                new_boxes = set(current_boxes)
                new_boxes.remove(next_p)
                new_boxes.add(next_box)
                new_boxes = frozenset(new_boxes)
            else:
                new_boxes = current_boxes

            next_state = (next_p, new_boxes)
            if next_state not in visited:
                visited.add(next_state)
                queue.append(next_state)
    return False


def generate_valid_sokoban_map(width=9, height=6, num_boxes=2):
    """클리어가 보장된 9x6 맵을 생성하여 반환하는 함수"""
    while True:
        grid = [[0] * width for _ in range(height)]

        # 1. 테두리 외벽 설치
        for x in range(width):
            grid[0][x] = 1
            grid[height - 1][x] = 1
        for y in range(height):
            grid[y][0] = 1
            grid[y][width - 1] = 1

        # 내부 빈 공간 좌표 추출
        empty_cells = [
            (x, y) for y in range(1, height - 1) for x in range(1, width - 1)
        ]

        # 2. 내부 장애물 벽 무작위 배치 (3~5개)
        num_inner_walls = random.randint(3, 5)
        inner_walls = random.sample(empty_cells, num_inner_walls)
        for x, y in inner_walls:
            grid[y][x] = 1
            empty_cells.remove((x, y))

        # 3. 목적지, 상자, 플레이어 배치 무작위 추출
        chosen = random.sample(empty_cells, num_boxes * 2 + 1)
        targets = chosen[:num_boxes]
        boxes = chosen[num_boxes : num_boxes * 2]
        player = chosen[num_boxes * 2]

        # 4. 검증을 위한 벽 정보 셋팅
        walls_set = {
            (x, y) for y in range(height) for x in range(width) if grid[y][x] == 1
        }

        # 5. 솔버 검증 통과 시 데이터 최종 변환 후 출력
        if solve_sokoban_quick(
            width, height, walls_set, frozenset(targets), frozenset(boxes), player
        ):
            for x, y in targets:
                grid[y][x] = 2
            for x, y in boxes:
                grid[y][x] = 3
            grid[player[1]][player[0]] = 4
            return grid


# 실행 및 결과 확인
new_map = generate_valid_sokoban_map(width=9, height=6, num_boxes=3)
print("🎉 클리어가 100% 보장되는 새로운 9x6 맵이 생성되었습니다:\n")
for row in new_map:
    print(row)
