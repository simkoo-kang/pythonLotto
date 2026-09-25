import random
import pygame
from game.jewel.settings import (BOMB_BONUS, CELL_SIZE, COLORS, DEFAULT_SCORE, EMPTY_COLOR,
    GRID_SIZE, MISSILE_BONUS, PROPELLER_BONUS, RAINBOW_BONUS, SCORE_PANEL_HEIGHT)
from cell import Cell, create_cell_by_type


class Board:
    def __init__(self):
        self.grid = self.generate_grid()
        self.score_unit = DEFAULT_SCORE

    def check_initial_matches(self, g):
        """
        보드가 16x16, 24x24 등으로 거대해지더라도 가로/세로/ㅁ자 사각형 매칭을
        완벽하게 추적하여 초기 화면에 맞춰진 보석이 단 하나도 없도록 필터링합니다.
        """
        # 1. 거대 보드판 전 구역 가로 일렬 3개 매칭 스캔
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE - 2):
                if g[r][c] == g[r][c+1] == g[r][c+2]: 
                    return True
                    
        # 2. 거대 보드판 전 구역 세로 일렬 3개 매칭 스캔
        for r in range(GRID_SIZE - 2):
            for c in range(GRID_SIZE):
                if g[r][c] == g[r+1][c] == g[r+2][c]: 
                    return True
                    
        # 3. 거대 보드판 전 구역 ㅁ자 네모 사각형 (2x2) 매칭 사전 차단 스캔
        for r in range(GRID_SIZE - 1):
            for c in range(GRID_SIZE - 1):
                if g[r][c] == g[r][c+1] == g[r+1][c] == g[r+1][c+1]: 
                    return True
                    
        return False

    def generate_grid(self):
        """
        보드판이 16x16, 24x24 등으로 거대해지더라도 무한 루프(렉) 없이
        0.001초 만에 초기 매칭이 단 하나도 없는 완벽한 보드를 실시간으로 빌드합니다.
        """
        # GRID_SIZE 크기의 빈 색상 매트릭스 생성
        temp = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # 현재 칸에 넣을 수 있는 유효한 색상 후보군 리스트 (복사본)
                valid_colors = list(COLORS)
                
                while valid_colors:
                    chosen_color = random.choice(valid_colors)
                    
                    # 1. 가로 3줄 매칭 회피 검사
                    if c >= 2 and temp[r][c-1] == chosen_color and temp[r][c-2] == chosen_color:
                        valid_colors.remove(chosen_color)
                        continue
                        
                    # 2. 세로 3줄 매칭 회피 검사
                    if r >= 2 and temp[r-1][c] == chosen_color and temp[r-2][c] == chosen_color:
                        valid_colors.remove(chosen_color)
                        continue
                        
                    # 3. ㅁ자 사각형(2x2) 매칭 회피 검사
                    if r >= 1 and c >= 1 and temp[r-1][c] == chosen_color and temp[r][c-1] == chosen_color and temp[r-1][c-1] == chosen_color:
                        valid_colors.remove(chosen_color)
                        continue
                    
                    # 세 가지 회피 검사를 모두 통과했다면 이 색상으로 확정 배정 후 탈출
                    temp[r][c] = chosen_color
                    break
                
                # 혹시라도 색상이 고갈되는 예외 상황이 발생하면 임의의 색상 배치
                if temp[r][c] is None:
                    temp[r][c] = random.choice(COLORS)
                    
        # 실시간 매칭 회피 조립이 끝난 안전한 temp 데이터를 기반으로 진짜 Cell 객체 격자 생성 후 즉시 리턴
        return [[Cell(temp[r][c], r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

    def update_cells(self):
        animating = False
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].update():
                    animating = True
        return animating

    def analyze_matches(self):
        h_lines, v_lines, squares = [], [], []
        for r in range(GRID_SIZE):
            c = 0
            while c < GRID_SIZE - 2:
                if self.grid[r][c].color != EMPTY_COLOR:
                    l = 1
                    while (
                        c + l < GRID_SIZE
                        and self.grid[r][c].color == self.grid[r][c + l].color
                    ):
                        l += 1
                    if l >= 3:
                        h_lines.append(
                            {"cells": [(r, c + i) for i in range(l)], "len": l}
                        )
                        c += l
                        continue
                c += 1
        for c in range(GRID_SIZE):
            r = 0
            while r < GRID_SIZE - 2:
                if self.grid[r][c].color != EMPTY_COLOR:
                    l = 1
                    while (
                        r + l < GRID_SIZE
                        and self.grid[r][c].color == self.grid[r + l][c].color
                    ):
                        l += 1
                    if l >= 3:
                        v_lines.append(
                            {"cells": [(r + i, c) for i in range(l)], "len": l}
                        )
                        r += l
                        continue
                r += 1
        for r in range(GRID_SIZE - 1):
            for c in range(GRID_SIZE - 1):
                color = self.grid[r][c].color
                if (
                    color != EMPTY_COLOR
                    and self.grid[r][c + 1].color == color
                    and self.grid[r + 1][c].color == color
                    and self.grid[r + 1][c + 1].color == color
                ):
                    squares.append([(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)])

        to_destroy, items = set(), []
        used_h, used_v = set(), set()

        for idx, h in enumerate(h_lines):
            if h["len"] >= 5 and idx not in used_h:
                used_h.add(idx)
                to_destroy.update(h["cells"])
                br, bc = h["cells"][h["len"] // 2]
                items.append(
                    {"r": br, "c": bc, "color": (255, 255, 255), "type": "RAINBOW"}
                )
        for idx, v in enumerate(v_lines):
            if v["len"] >= 5 and idx not in used_v:
                used_v.add(idx)
                to_destroy.update(v["cells"])
                br, bc = v["cells"][v["len"] // 2]
                items.append(
                    {"r": br, "c": bc, "color": (255, 255, 255), "type": "RAINBOW"}
                )
        for hi, h in enumerate(h_lines):
            if hi in used_h:
                continue
            for vi, v in enumerate(v_lines):
                if vi in used_v:
                    continue
                inter = set(h["cells"]).intersection(set(v["cells"]))
                if inter:
                    used_h.add(hi)
                    used_v.add(vi)
                    to_destroy.update(h["cells"])
                    to_destroy.update(v["cells"])
                    inter_list = list(inter)
                    if inter_list:
                        cr, cc = inter_list[0]
                        items.append(
                            {
                                "r": cr,
                                "c": cc,
                                "color": self.grid[cr][cc].color,
                                "type": "BOMB",
                            }
                        )
        for idx, h in enumerate(h_lines):
            if h["len"] == 4 and idx not in used_h:
                used_h.add(idx)
                to_destroy.update(h["cells"])
                br, bc = h["cells"][0]
                items.append(
                    {
                        "r": br,
                        "c": bc,
                        "color": self.grid[br][bc].color,
                        "type": "V_MISSILE",
                    }
                )
        for idx, v in enumerate(v_lines):
            if v["len"] == 4 and idx not in used_v:
                used_v.add(idx)
                to_destroy.update(v["cells"])
                br, bc = v["cells"][0]
                items.append(
                    {
                        "r": br,
                        "c": bc,
                        "color": self.grid[br][bc].color,
                        "type": "H_MISSILE",
                    }
                )
        for sq in squares:
            if not set(sq).intersection(to_destroy):
                to_destroy.update(sq)
                sr, sc = sq[0]
                items.append(
                    {
                        "r": sr,
                        "c": sc,
                        "color": self.grid[sr][sc].color,
                        "type": "PROPELLER",
                    }
                )
        for h in h_lines:
            to_destroy.update(h["cells"])
        for v in v_lines:
            to_destroy.update(v["cells"])
        return list(to_destroy), items

    def trigger_item_effect(
        self,
        r,
        c,
        item_type,
        rainbow_target_color,
        exploded_set,
        rainbow_item_target="NORMAL",
        processed_set=None,
    ):
        if processed_set is None:
            processed_set = set()
        if (r, c) in processed_set:
            return
        processed_set.add((r, c))

        if item_type == "H_MISSILE":
            self.score_unit += MISSILE_BONUS
            for i in range(GRID_SIZE):
                exploded_set.add((r, i))
                if (
                    self.grid[r][i].item_type != "NORMAL"
                    and (r, i) not in processed_set
                ):
                    self.trigger_item_effect(
                        r,
                        i,
                        self.grid[r][i].item_type,
                        self.grid[r][i].color,
                        exploded_set,
                        rainbow_item_target,
                        processed_set,
                    )
        elif item_type == "V_MISSILE":
            self.score_unit += MISSILE_BONUS
            for i in range(GRID_SIZE):
                exploded_set.add((i, c))
                if (
                    self.grid[i][c].item_type != "NORMAL"
                    and (i, c) not in processed_set
                ):
                    self.trigger_item_effect(
                        i,
                        c,
                        self.grid[i][c].item_type,
                        self.grid[i][c].color,
                        exploded_set,
                        rainbow_item_target,
                        processed_set,
                    )
        elif item_type == "BOMB":
            self.score_unit += BOMB_BONUS
            for i in range(max(0, r - 2), min(GRID_SIZE, r + 3)):
                for j in range(max(0, c - 2), min(GRID_SIZE, c + 3)):
                    exploded_set.add((i, j))
                    if (
                        self.grid[i][j].item_type != "NORMAL"
                        and (i, j) not in processed_set
                    ):
                        self.trigger_item_effect(
                            i,
                            j,
                            self.grid[i][j].item_type,
                            self.grid[i][j].color,
                            exploded_set,
                            rainbow_item_target,
                            processed_set,
                        )
        elif item_type == "PROPELLER":
            self.score_unit += PROPELLER_BONUS
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    exploded_set.add((nr, nc))
                    if (
                        self.grid[nr][nc].item_type != "NORMAL"
                        and (nr, nc) not in processed_set
                    ):
                        self.trigger_item_effect(
                            nr,
                            nc,
                            self.grid[nr][nc].item_type,
                            self.grid[nr][nc].color,
                            exploded_set,
                            rainbow_item_target,
                            processed_set,
                        )
            valid = [
                (i, j)
                for i in range(GRID_SIZE)
                for j in range(GRID_SIZE)
                if (i, j) not in exploded_set
                and self.grid[i][j].color != EMPTY_COLOR
                and self.grid[i][j].color in COLORS
            ]
            if valid:
                tr, tc = random.choice(valid)
                exploded_set.add((tr, tc))
                if (
                    self.grid[tr][tc].item_type != "NORMAL"
                    and (tr, tc) not in processed_set
                ):
                    self.trigger_item_effect(
                        tr,
                        tc,
                        self.grid[tr][tc].item_type,
                        self.grid[tr][tc].color,
                        exploded_set,
                        rainbow_item_target,
                        processed_set,
                    )
        elif item_type == "RAINBOW":
            self.score_unit += RAINBOW_BONUS
            if rainbow_item_target != "NORMAL":
                valid_spots = []
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        if (
                            self.grid[i][j].item_type == "NORMAL"
                            and self.grid[i][j].color != EMPTY_COLOR
                        ):
                            valid_spots.append((i, j))
                spawn_count = min(len(valid_spots), random.randint(6, 9))
                chosen_spots = (
                    random.sample(valid_spots, spawn_count) if valid_spots else []
                )
                for sr, sc in chosen_spots:
                    self.grid[sr][sc].item_type = rainbow_item_target
                    exploded_set.add((sr, sc))
                    self.trigger_item_effect(
                        sr,
                        sc,
                        rainbow_item_target,
                        self.grid[sr][sc].color,
                        exploded_set,
                        "NORMAL",
                        processed_set,
                    )
            else:
                if rainbow_target_color == (255, 255, 255):
                    counts = {}
                    for i in range(GRID_SIZE):
                        for j in range(GRID_SIZE):
                            c_color = self.grid[i][j].color
                            if c_color != EMPTY_COLOR and c_color in COLORS:
                                counts[c_color] = counts.get(c_color, 0) + 1
                    target = (
                        max(counts, key=counts.get) if counts else random.choice(COLORS)
                    )
                else:
                    target = rainbow_target_color
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        if self.grid[i][j].color == target:
                            exploded_set.add((i, j))
                            if (
                                self.grid[i][j].item_type != "NORMAL"
                                and (i, j) not in processed_set
                            ):
                                self.trigger_item_effect(
                                    i,
                                    j,
                                    self.grid[i][j].item_type,
                                    self.grid[i][j].color,
                                    exploded_set,
                                    "NORMAL",
                                    processed_set,
                                )
        for pr, pc in exploded_set:
            self.grid[pr][pc].is_destroying = True

    def apply_fall(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c].is_destroying or self.grid[r][c].alpha <= 0:
                    self.grid[r][c].color, self.grid[r][c].item_type = (
                        EMPTY_COLOR,
                        "NORMAL",
                    )
                    self.grid[r][c].is_destroying, self.grid[r][c].alpha = False, 255
        for c in range(GRID_SIZE):
            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c].color == EMPTY_COLOR:
                    for k in range(r - 1, -1, -1):
                        if self.grid[k][c].color != EMPTY_COLOR:
                            self.grid[r][c], self.grid[k][c] = (
                                self.grid[k][c],
                                self.grid[r][c],
                            )
                            break
            for r in range(GRID_SIZE):
                if self.grid[r][c].color == EMPTY_COLOR:
                    self.grid[r][c] = Cell(random.choice(COLORS), r, c)
                    self.grid[r][c].y = SCORE_PANEL_HEIGHT - CELL_SIZE
                self.grid[r][c].r, self.grid[r][c].c = r, c
                self.grid[r][c].target_x, self.grid[r][c].target_y = (
                    c * CELL_SIZE,
                    r * CELL_SIZE + SCORE_PANEL_HEIGHT,
                )
