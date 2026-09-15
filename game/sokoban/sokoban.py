from collections import deque
import json
import os
from pathlib import Path
import random
import re

from class_main import ClassMain


class Sokoban(ClassMain):
    def __init__(self, file_path: str = None, file_name: str = "sokoban.json"):
        super().__init__()

        filepath = Path(__file__).parent if file_path == None else file_path

        self.fullpath = os.path.join(filepath, file_name)
        if os.path.exists(self.fullpath):
            with open(self.fullpath, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            self.records = self.data["records"]
            self.list: list = self.data["list"]
        else:
            self.data = {"records": 0, "list": []}
            self.records = self.data["records"]
            self.list: list = self.data["list"]
            self.save()

        """_summary_
        대용량일 때, 데이터가 매우 많은 경우
        # 1. 프로그램 시작 시, 기존 matrix 데이터들을 set으로 빌드 (O(N) 최초 1회)
        """
        # self.existing_matrices_set = {self.to_tuple(item["matrix"]) for item in self.list}

    def save(self):

        # 1. 먼저 전체 데이터를 예쁘게 들여쓰기된 문자열로 바꿉니다.
        json_string = json.dumps(
            {"records": self.records, "list": self.list},
            indent=4,
            ensure_ascii=False,
        )

        # 2. 정규식을 이용해 1차원 숫자 배열 내부의 줄바꿈과 공백을 한 줄로 압축합니다.
        # [ 1, 2, ... ] 형태를 찾아서 대괄호 안의 공백과 줄바꿈을 지워줍니다.
        clean_json_string = re.sub(
            r"\[\s+([\d,\s]+)\s+\]",
            lambda m: "[" + re.sub(r"\s+", "", m.group(1)) + "]",
            json_string,
        )

        # 3. 압축된 문자열을 파일에 그대로 씁니다.
        with open(self.fullpath, "w", encoding="utf-8") as f:
            f.write(clean_json_string)

    def __check_sokoban_quick(
        self, width, height, walls, targets, initial_boxes, start_player
    ) -> bool:
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
                if (
                    (up and left)
                    or (up and right)
                    or (down and left)
                    or (down and right)
                ):
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

    # 0: 바닥, 1: 벽, 2: 목적지, 3: 상자, 4: 플레이어
    # 5: 목적지 위의 상자 (상자3 + 목적지2) -> 초기 배치에 있을 수 있으므로 포함
    def analyze_map(self, grid):
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

        return width, height, walls, targets, boxes, player_pos

    def check_sokoban(self, map_data) -> bool:
        width, height, walls, targets, boxes, player_pos = self.analyze_map(map_data)
        return self.__check_sokoban_quick(
            width, height, walls, frozenset(targets), frozenset(boxes), player_pos
        )

    def contains_matrix(self, matrix):
        return any(item.get("matrix") == matrix for item in self.list)

    def to_tuple(self, matrix):
        return tuple(tuple(row) for row in matrix)

    """_summary_
    대용량일 때, 데이터가 매우 많은 경우 init함수에서 한 번 실행 후 다음 진행
    # 1. 프로그램 시작 시, 기존 matrix 데이터들을 set으로 빌드 (O(N) 최초 1회)
    """
    # def contains_matrix_large_data(self, matrix):
    #     # 2. 새로운 데이터가 들어왔을 때 중복 체크 (O(1) - 데이터가 많아도 즉시 확인)
    #     new_matrix_tuple = self.to_tuple(matrix)

    #     return new_matrix_tuple in self.existing_matrices_set

    def generate_valid_sokoban_map(
        self,
        width,
        height,
        num_boxes: int = 2,
        obstacle: list[int] = [3, 5],
        tried: int = 100000,
    ):
        """클리어가 보장된 9x6 맵을 생성하여 반환하는 함수"""
        total = 0
        while total < tried:
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
            num_inner_walls = random.randint(obstacle[0], obstacle[1])
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
            if self.__check_sokoban_quick(
                width, height, walls_set, frozenset(targets), frozenset(boxes), player
            ):
                for x, y in targets:
                    grid[y][x] = 2
                for x, y in boxes:
                    grid[y][x] = 3
                grid[player[1]][player[0]] = 4
                if not self.contains_matrix(grid):
                    result, path = self.solve_sokoban(grid)
                    if result:
                        self.list.append({"matrix": grid, "path": path})
                        self.records = len(self.list)
                        self.save()
                        return grid, path
            total += 1

    def solve_sokoban(self, grid):
        if self.contains_matrix(grid):
            return False, "❌ 이미 존재하는 조합입니다."

        width, height, walls, targets, initial_boxes, start_player = self.analyze_map(
            grid
        )
        initial_boxes = frozenset(initial_boxes)
        targets = frozenset(targets)

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
                if (
                    (up and left)
                    or (up and right)
                    or (down and left)
                    or (down and right)
                ):
                    corner_deadlocks.add((x, y))

        # BFS 탐색 시작 설정
        start_state = (start_player, initial_boxes)
        queue = deque([(start_state, "")])  # (상태, 이동 경로 문자열)
        visited = {start_state}

        directions = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}

        self.logger.debug("🔍 9x6 맵 분석 및 검증을 시작합니다...")

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

        return (
            False,
            "❌ 클리어가 절대 불가능한 맵(데드락 맵)입니다! 맵을 수정해 주세요.",
        )


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    width, height, box_count = 9, 6, 3

    test_map = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 0, 0, 1, 1, 1],
        [1, 0, 2, 0, 3, 1, 0, 1, 1],
        [1, 0, 3, 0, 3, 4, 1, 0, 1],
        [1, 0, 2, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    sokoban = Sokoban("./game/sokoban", "sokoban.json")
    if sokoban.check_sokoban(test_map):
        sokoban.logger.debug("성공 ==========================")
        result, path = sokoban.solve_sokoban(test_map)
        if result:
            sokoban.logger.debug(
                f"✅ 클리어 가능한 맵입니다!\n🎯 최단 이동 경로: {path} (총 {len(path)}걸음)"
            )
        else:
            sokoban.logger.debug(path)
    else:
        sokoban.logger.debug("실패 --------------------------")

    new_map, path = sokoban.generate_valid_sokoban_map(
        width=width, height=height, num_boxes=5, obstacle=[4, 6], tried=200000
    )

    sokoban.logger.debug(
        "\n🎉 클리어가 100% 보장되는 새로운 9x6 맵이 생성되었습니다:\n"
    )
    for row in new_map:
        sokoban.logger.debug(row)

    sokoban.logger.debug(path)
