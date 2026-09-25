from collections import deque
import copy

# 테스트용 9x6 맵 데이터 (가로 9칸, 세로 6칸)
# 0: 바닥, 1: 벽, 2: 목적지, 3: 상자, 4: 플레이어
# 5: 목적지 위의 상자 (상자3 + 목적지2) -> 초기 배치에 있을 수 있으므로 포함
# TEST_MAP = [
#     [1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 4, 0, 0, 0, 1],
#     [1, 0, 0, 2, 1, 0, 2, 0, 1],
#     [1, 0, 3, 0, 3, 0, 3, 0, 1],
#     [1, 0, 2, 1, 1, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1, 1]
# ]

TEST_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 1, 1, 1],
    [1, 0, 2, 0, 3, 1, 0, 1, 1],
    [1, 0, 3, 0, 3, 4, 1, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
]


def analyze_map(grid):
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    walls = set()
    targets = set()
    boxes = set()
    player_pos = None

    for y in range(height):
        for x in range(width):
            val = grid[y][x]
            if val == 1:
                walls.add((x, y))
            elif val == 2:
                targets.add((x, y))
            elif val == 3:
                boxes.add((x, y))
            elif val == 4:
                player_pos = (x, y)
            elif val == 5:
                targets.add((x, y))
                boxes.add((x, y))

    return width, height, walls, targets, frozenset(boxes), player_pos


def solve_sokoban(grid):
    width, height, walls, targets, initial_boxes, start_player = analyze_map(grid)

    if not start_player:
        return False, "❌ 플레이어(4) 위치가 맵에 존재하지 않습니다."
    if not targets:
        return False, "❌ 목적지(2) 위치가 맵에 존재하지 않습니다."
    if len(initial_boxes) != len(targets):
        return (
            False,
            f"❌ 상자 개수({len(initial_boxes)})와 목적지 개수({len(targets)})가 일치하지 않습니다.",
        )

    # 정적 코너 데드락 감지 (구석자리 판정)
    corner_deadlocks = set()
    for y in range(height):
        for x in range(width):
            if (x, y) in walls or (x, y) in targets:
                continue
            up = (x, y - 1) in walls
            down = (x, y + 1) in walls
            left = (x - 1, y) in walls
            right = (x + 1, y) in walls
            if (up and left) or (up and right) or (down and left) or (down and right):
                corner_deadlocks.add((x, y))

    # BFS 탐색 시작 설정
    start_state = (start_player, initial_boxes)
    queue = deque([(start_state, "")])  # (상태, 이동 경로 문자열)
    visited = {start_state}

    directions = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}

    print("🔍 9x6 맵 분석 및 검증을 시작합니다...")

    # --- 깔끔하게 정리된 메인 탐색 루프 ---
    while queue:
        (curr_player, current_boxes), path = queue.popleft()
        p_x, p_y = curr_player

        # 승리 조건 검사: 모든 상자가 목적지에 도착했는가?
        if current_boxes == targets:
            return True, path

        for cmd, (dx, dy) in directions.items():
            next_p = (p_x + dx, p_y + dy)

            # 이동할 자리가 벽이면 이동 불가
            if next_p in walls:
                continue

            # 이동할 자리에 상자가 있는 경우
            if next_p in current_boxes:
                # 튜플의 x, y 요소를 각각 꺼내어 방향(dx, dy)을 더해줍니다.
                next_box = (next_p[0] + dx, next_p[1] + dy)

                # 상자가 밀려날 곳이 벽이거나 다른 상자가 있으면 밀 수 없음
                if next_box in walls or next_box in current_boxes:
                    continue

                # 목적지가 아닌 구석(데드락 타일)으로 상자가 들어가면 패스
                if next_box in corner_deadlocks:
                    continue

                # 상자 위치 갱신
                new_boxes = set(current_boxes)
                new_boxes.remove(next_p)
                new_boxes.add(next_box)
                new_boxes = frozenset(new_boxes)
            else:
                # 빈 바닥 이동 시 상자 위치는 그대로
                new_boxes = current_boxes

            next_state = (next_p, new_boxes)

            # 처음 탐색하는 배치 상태라면 큐에 추가
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + cmd))

    return False, ""


# 실행
is_solvable, path = solve_sokoban(TEST_MAP)
print("-" * 50)
if is_solvable:
    print(f"✅ 클리어 가능한 맵입니다!\n🎯 최단 이동 경로: {path} (총 {len(path)}걸음)")
else:
    print("❌ 클리어가 절대 불가능한 맵(데드락 맵)입니다! 맵을 수정해 주세요.")
print("-" * 50)
