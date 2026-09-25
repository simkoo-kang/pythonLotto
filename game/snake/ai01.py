# ai.py
from collections import deque
from game.snake.models import GRID_WIDTH, GRID_HEIGHT

class SnakeAI:
    """8자 뺑뺑이를 차단하고, 필요할 때만 구불구불 우회하는 밸런스형 지그재그 AI"""

    def bfs_smart_path(self, snake_body, start, target, current_dir):
        """
        거리(이동 횟수)를 최우선으로 하되, 거리가 같다면 
        벽면이나 몸통 충돌을 방지하기 위해 '약간의 지그재그'를 적용합니다.
        """
        # start가 리스트(몸통 전체)라면 무조건 0번째 머리 튜플만 강제로 추출합니다.
        if isinstance(start, list) and len(start) > 0:
            start = start[0]
            
        queue = deque([(start, current_dir, [])])
        visited = {start}
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)] # 상, 하, 좌, 우

        while queue:
            current, last_dir, path = queue.popleft()

            if current == target:
                return path

            # 직진 방향을 배열의 앞으로 당겨서 탐색 우선순위를 줍니다. (8자 제자리 춤 방지)
            sorted_dirs = list(directions)
            if last_dir in sorted_dirs:
                sorted_dirs.remove(last_dir)
                sorted_dirs.insert(0, last_dir)

            for dx, dy in sorted_dirs:
                # [💡 핵심 교정 1] 튜플의 인덱스([0], [1])로 접근하여 정수형 역방향을 올바르게 검사합니다.
                if dx == -last_dir[0] and dy == -last_dir[1]:
                    continue

                next_node = (current[0] + dx, current[1] + dy)

                # X, Y 좌표를 각각 인덱스로 분리하여 정수(int)끼리 올바르게 크기 비교를 합니다.
                if (0 <= next_node[0] < GRID_WIDTH and 
                    0 <= next_node[1] < GRID_HEIGHT and 
                    next_node not in visited):
                    
                    if next_node in snake_body[:-1]:
                        continue

                    visited.add(next_node)
                    queue.append((next_node, (dx, dy), path + [next_node]))

        return None

    def decide_direction(self, snake_list, food_pos, current_dir):
        """[밸런스 통제 타워] 8자 데드락을 풀고 기회를 포착합니다."""
        # snake_list(리스트)의 '0번째 인덱스'인 머리 튜플을 확실하게 꺼냅니다.
        head = snake_list[0] if isinstance(snake_list, list) and len(snake_list) > 0 else snake_list
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        # 1. 먹이로 가는 스마트 경로가 존재하는지 확인
        shortest_path = self.bfs_smart_path(snake_list, head, food_pos, current_dir)
        
        if shortest_path:
            next_step = shortest_path[0]
            
            # 가상 시뮬레이션으로 먹이를 끝까지 먹어봄
            virtual_snake = list(snake_list)
            for step in shortest_path:
                virtual_snake.insert(0, step)
                if step == food_pos:
                    pass
                else:
                    virtual_snake.pop()
            
            # [💡 핵심 교정 2] 파이썬에서 금지된 튜플 간 직접 뺄셈을 피하고, 각 인덱스 요소별로 빼서 방향 벡터를 만듭니다.
            sim_dir = (next_step[0] - head[0], next_step[1] - head[1])
            
            # 먹이를 먹은 시점에 진짜 내 꼬리를 물고 빠져나올 수 있는가?
            path_to_tail = self.bfs_smart_path(virtual_snake, shortest_path[-1], virtual_snake[-1], sim_dir)
            
            if path_to_tail:
                # 8자 뺑뺑이를 돌지 않고 과감하게 먹이 사냥 터치 다운!
                return sim_dir

        # 2. 사냥 경로가 없거나 위험하다면 내 꼬리를 우회하며 추적
        best_move = current_dir
        max_dist = -1

        for dx, dy in directions:
            # [💡 핵심 교정 3] 여기서도 현재 방향의 역방향 검사를 튜플 인덱싱으로 정정합니다.
            if dx == -current_dir[0] and dy == -current_dir[1]:
                continue
                
            next_node = (head[0] + dx, head[1] + dy)
            if (0 <= next_node[0] < GRID_WIDTH and 
                0 <= next_node[1] < GRID_HEIGHT and 
                next_node not in snake_list[:-1]):
                
                virtual_snake = [next_node] + snake_list[:-1]
                tail_path = self.bfs_smart_path(virtual_snake, next_node, virtual_snake[-1], (dx, dy))
                
                if tail_path and len(tail_path) > max_dist:
                    # 꼬리를 쫓을 때는 공간을 크게 넓히기 위해 가장 멀리 돌아서(우회해서) 쫓아감
                    max_dist = len(tail_path)
                    best_move = (dx, dy)

        return best_move
