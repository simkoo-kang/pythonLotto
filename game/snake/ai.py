# ai.py
from collections import deque
import copy


"""
AI는 매 프레임(찰나의 순간)마다 아래의 우선순위에 따라 어떤 방향으로 꺾을지 치열하게 고민합니다.
1단계: 먹이 사냥 가능 여부 검증 (사냥 모드)논리:
     "먹이로 가는 가장 빠른 길(최단거리 BFS)이 있나? 있다면,
     그 길을 따라가서 먹이를 먹은 미래 시점에도 내 늘어난 꼬리(탈출구)를 안전하게 붙잡을 수 있는가?
  - "결과: 만약 먹이를 먹고 나서도 꼬리로 가는 길이 열려있다면 사냥을 승인하고 그 방향으로 전진합니다.
2단계: 꼬리 추적 (안전 생존 모드)논리:
     "1단계 검증을 해보니 먹이를 먹으면 몸이 굳어서 갇히겠네?
     혹은 먹이로 가는 길 자체가 장애물에 막혔네? 사냥 금지!
     지금은 살아야 하니까 내 진짜 꼬리 끝점을 향해 도망치자.
  - "결과: 주변 4방향 중 내 몸통을 우회하여 꼬리선으로 가장 안전하게 이어지는 방향을 선택해 똬리를 틀며 버팁니다.
3단계: 임시 버티기 (최후의 비상 탈출)논리:
     "큰일 났다. 장애물과 내 몸통 사이에 끼어서 먹이로도 못 가고, 내 꼬리로 가는 길도 끊겼다.
     사방이 벽이다!
  - "결과: 당장 다음 칸에 부딪혀 죽는 것을 막기 위해, 주변 4칸 중 '그나마 숨통이 가장 많이 트인 빈 공간(자유도가 높은 칸)'을 찾아 임시로 대피합니다.
    (이번 조기 사망은 이 3단계 계산 과정에서 좌표 자료형이 뒤틀려 엉뚱한 벽으로 돌진했기 때문입니다.)
"""

class SnakeAI:
    """깊은 복사(Deepcopy)를 도입하여 시뮬레이션 데이터 오염을 원천 차단한 AI"""

    def bfs_smart_path(self, snake_body, start, target, current_dir):
        # start가 리스트라면 0번째 머리 튜플만 추출
        if isinstance(start, list) and len(start) > 0:
            start = start[0]
            
        queue = deque([(start, current_dir, [])])
        visited = {start}
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)] # 상, 하, 좌, 우

        # [💡 완벽 고정] 400x400 창 기준 20격자 규격 (안전 규격 보장)
        grid_w, grid_h = 20, 20

        while queue:
            current, last_dir, path = queue.popleft()

            if current == target:
                return path

            # 직진보다 회전을 우선 탐색하여 대각선 무빙 유도
            sorted_dirs = list(directions)
            if last_dir in sorted_dirs:
                sorted_dirs.remove(last_dir)
                sorted_dirs.append(last_dir)

            for dx, dy in directions:
                if dx == -last_dir[0] and dy == -last_dir[1]:
                    continue

                next_node = (current[0] + dx, current[1] + dy)

                # X, Y 좌표 요소를 정수형태로 올바르게 비교 검사
                if (0 <= next_node[0] < grid_w and 
                    0 <= next_node[1] < grid_h and 
                    next_node not in visited):
                    
                    if next_node in snake_body[:-1]:
                        continue

                    visited.add(next_node)
                    queue.append((next_node, (dx, dy), path + [next_node]))

        return None

    def count_open_space(self, snake_body, pos):
        """특정 위치 주변의 숨통이 트인 빈 격자 개수를 측정"""
        count = 0
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            n_node = (pos + dx, pos + dy)
            if (0 <= n_node[0] < 20 and 0 <= n_node[1] < 20 and n_node not in snake_body):
                count += 1
        return count

    def decide_direction(self, snake_list, food_pos, current_dir):
        """[완전 독립 샌드박스 통제 타워]"""
        # snake_list에서 확실하게 머리 튜플만 추출합니다.
        head = snake_list[0] if isinstance(snake_list, list) and len(snake_list) > 0 else snake_list
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        # 1. 먹이 경로 탐색
        shortest_path = self.bfs_smart_path(snake_list, head, food_pos, current_dir)
        
        if shortest_path and len(shortest_path) > 0:
            next_step = shortest_path
            
            # 깊은 복사(deepcopy)로 실제 인게임 데이터 보호구역 지정
            virtual_snake = copy.deepcopy(snake_list)
            for step in shortest_path:
                virtual_snake.insert(0, step)
                if step == food_pos:
                    pass
                else:
                    virtual_snake.pop()
            
            # 정수 뺄셈 연산으로 안전하게 방향 벡터 추출
            sim_dir = (next_step[0][0] - head[0], next_step[0][1] - head[1])
            path_to_tail = self.bfs_smart_path(virtual_snake, shortest_path[-1], virtual_snake[-1], sim_dir)
            
            if path_to_tail:
                return sim_dir

        # 2. 안전 확보용 꼬리 우회 추적
        best_move = current_dir
        max_dist = -1

        for dx, dy in directions:
            if dx == -current_dir[0] and dy == -current_dir[1]:
                continue
                
            next_node = (head[0] + dx, head[1] + dy)
            if (0 <= next_node[0] < 20 and 0 <= next_node[1] < 20 and next_node not in snake_list[:-1]):
                
                virtual_snake = copy.deepcopy(snake_list[:-1])
                virtual_snake.insert(0, next_node)
                tail_path = self.bfs_smart_path(virtual_snake, next_node, virtual_snake[-1], (dx, dy))
                
                if tail_path and len(tail_path) > max_dist:
                    max_dist = len(tail_path)
                    best_move = (dx, dy)

        # 3. 비상 상황: 가장 숨통이 많이 트인 칸 선택
        if max_dist == -1:
            best_safe_move = current_dir
            max_open = -1
            
            for dx, dy in directions:
                if dx == -current_dir[0] and dy == -current_dir[1]:
                    continue
                next_node = (head[0] + dx, head[1] + dy)
                if (0 <= next_node[0] < 20 and 0 <= next_node[1] < 20 and next_node not in snake_list[:-1]):
                    
                    open_count = self.count_open_space(snake_list, next_node)
                    if open_count > max_open:
                        max_open = open_count
                        best_safe_move = (dx, dy)
            
            return best_safe_move

        return best_move
