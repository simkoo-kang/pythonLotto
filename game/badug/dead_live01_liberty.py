"""
🚀 바둑 사활 로직 개발 4단계 로드맵
1단계: 바둑판과 '활로(Liberty)' 계산 로직 만들기 (기초)
 - 사활의 가장 기본은 "돌이 잡혔는가?"를 판단하는 것입니다.
 1. 목표: 바둑판(2차원 배열)에 돌을 놓았을 때, 연결된 돌들의 활로(숨구멍) 개수를 계산하는 코드를 짭니다.
 2. 핵심 알고리즘: BFS(너비 우선 탐색) 또는 DFS(깊이 우선 탐색) 알고리즘을 사용해 상하좌우로 연결된 같은 색 돌의 덩어리(그룹)를 찾고,
    그 덩어리 주변의 빈 공간을 카운트합니다.
 3. 결과: 활로가 0개가 되면 바둑판에서 돌을 들어내는(따내는) 규칙을 구현합니다.

2단계: '착수 금지'와 '패(Ko)' 규칙 구현하기 (완전한 바둑판)
 - 사활 문제는 착수 금지 공간을 이용해 집을 만드는 경우가 많습니다.
 1. 목표: 바둑판에 돌을 놓을 수 있는 자리와 없는 자리를 구별합니다.
 2. 착수 금지: 활로가 0개인 곳에는 돌을 놓을 수 없지만, 그 수로 인해 상대방 돌을 따낼 수 있다면 놓을 수 있는 예외 처리를 만듭니다.
 3. 패(Ko) 규칙: 바로 직전에 상대가 따낸 돌을 곧바로 다시 따낼 수 없도록 동형반복 금지 규칙을 추가합니다.

3단계: 미니 사활 자동 해석기(Solver) 만들기 (알고리즘)
 - 여기서부터 진짜 사활 문제 풀이 로직이 시작됩니다.
 1. 목표: 좁은 공간(예: 3x3, 4x4) 안에서 흑이 두면 살고, 백이 두면 죽는 정답을 컴퓨터가 스스로 연산하게 만듭니다.
 2. 핵심 알고리즘: 게임 이론에서 쓰이는 미니맥스(Minimax) 알고리즘과 알파-베타 가지치기(Alpha-Beta Pruning)를 사용합니다.
    흑은 내 돌의 활로와 집을 넓히는 최선의 수를 찾고, 백은 좁히는 최선의 수를 두어 끝까지 가상으로 두어보며 정답 수순을 찾아냅니다.

4단계: KataGo 엔진을 내 프로그램에 연동하기 (최종 단계)
 - 내가 만든 파이썬 프로그램에, 오늘 세팅하셨던 무적의 AI KataGo를 비서로 고용하는 단계입니다.
 1. 목표: 내가 직접 사활 정답을 계산하는 코드를 짜지 않고, KataGo에게 바둑판 상황을 던져주어 정답을 받아옵니다.
 2. 방법: 파이썬의 subprocess 라이브러리를 사용해 카타고 실행 파일(katago.exe)을 백그라운드로 켭니다.
    그리고 어제 적으셨던 name, play, genmove 같은 GTP 명령어를 코드로 카타고에게 보내 정답 좌표를 받아온 뒤,
    내 프로그램 화면에 띄워줍니다.
"""

from collections import deque


class BadukBoard:
    def __init__(self, size=9):
        self.size = size
        # 0: 빈칸, 1: 흑돌, 2: 백돌
        self.board = [[0] * size for _ in range(size)]

    def is_valid_coord(self, x, y):
        """좌표가 바둑판 내부인지 확인"""
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x, y):
        """상하좌우 인접 좌표 가져오기"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid_coord(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def find_group_and_liberties(self, start_x, start_y):
        """
        입력된 좌표의 돌과 연결된 같은 색 돌의 '덩어리'와 '활로 목록'을 찾음
        (BFS 알고리즘 활용)
        """
        stone_color = self.board[start_x][start_y]
        if stone_color == 0:
            return set(), set()

        queue = deque([(start_x, start_y)])
        group = {(start_x, start_y)}
        liberties = set()

        while queue:
            x, y = queue.popleft()
            for nx, ny in self.get_neighbors(x, y):
                if self.board[nx][ny] == 0:
                    # 빈칸이면 활로 목록에 추가
                    liberties.add((nx, ny))
                elif self.board[nx][ny] == stone_color and (nx, ny) not in group:
                    # 같은 색 돌이면 하나의 덩어리로 묶음
                    group.add((nx, ny))
                    queue.append((nx, ny))

        return group, liberties

    def remove_dead_stones(self, target_color):
        """바둑판 전체를 검사하여 활로가 0인 상대 돌들을 따냄(제거)"""
        visited = set()
        captured_count = 0

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == target_color and (x, y) not in visited:
                    # 덩어리와 활로 계산
                    group, liberties = self.find_group_and_liberties(x, y)
                    visited.update(group)

                    # 활로가 0개라면 돌을 들어냄 (따내기)
                    if len(liberties) == 0:
                        for gx, gy in group:
                            self.board[gx][gy] = 0  # 빈칸으로 변경
                            captured_count += 1

        return captured_count

    def print_board(self):
        """현재 바둑판 상태를 콘솔에 예쁘게 출력"""
        mapping = {0: " . ", 1: " ● ", 2: " ○ "}
        print("\n" + "=" * (self.size * 4))
        for row in self.board:
            print("".join([mapping[stone] for stone in row]))
        print("=" * (self.size * 4))


# ==========================================
# 🚀 알고리즘 작동 테스트 (단수 및 따내기)
# ==========================================
if __name__ == "__main__":
    # 1. 9x9 바둑판 생성
    game = BadukBoard(size=9)

    # 2. 중앙에 백돌 1개 배치 (좌표: 행4, 열4)
    game.board[4][4] = 2
    print("1. 백돌 1개를 중앙에 둡니다.")
    game.print_board()

    # 3. 흑이 백돌의 사방(활로 4개 중 3개)을 포위 (단수 상태 만들기)
    game.board[3][4] = 1  # 위
    game.board[5][4] = 1  # 아래
    game.board[4][3] = 1  # 왼쪽
    print("2. 흑돌 3개로 백을 포위하여 '단수'로 만듭니다.")
    game.print_board()

    # 4. 백의 남은 활로를 계산해보기
    _, liberties = game.find_group_and_liberties(4, 4)
    print(f"-> 현재 백돌의 남은 활로 좌표 목록: {liberties} (개수: {len(liberties)}개)")

    # 5. 흑이 마지막 남은 오른쪽 활로마저 막아서 따내기 처리
    print("\n3. 흑이 마지막 활로(오른쪽)를 막아 백을 따냅니다!")
    game.board[4][4 + 1] = 1  # 오른쪽 착수

    # 활로가 0이 된 백돌(2)을 검사해서 제거
    captured = game.remove_dead_stones(target_color=2)
    game.print_board()
    print(f"-> 따낸 백돌의 개수: {captured}개")
