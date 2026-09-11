# game_engine.py
from typing import List, Tuple, Optional
from piece import PuzzlePiece

class JigsawEngine:
    def __init__(self, rows: int, cols: int, piece_width: int, piece_height: int, start_x: int, start_y: int):
        self.rows = rows
        self.cols = cols
        self.piece_width = piece_width
        self.piece_height = piece_height
        self.start_x = start_x
        self.start_y = start_y
        self.pieces: List[PuzzlePiece] = []

    def reset(self, rows: int, cols: int, piece_width: int, piece_height: int, start_x: int, start_y: int):
        """[핵심 수정] 새 게임 시작 시 엔진의 모든 상태와 조각 배열을 완전히 초기화합니다."""
        self.rows = rows
        self.cols = cols
        self.piece_width = piece_width
        self.piece_height = piece_height
        self.start_x = start_x
        self.start_y = start_y
        self.pieces.clear()

    def register_piece(self, piece: PuzzlePiece):
        self.pieces.append(piece)

    def get_piece_by_id(self, canvas_id: int) -> Optional[PuzzlePiece]:
        for p in self.pieces:
            if p.id == canvas_id:
                return p
        return None

    def get_grid_pos_from_coords(self, x: float, y: float) -> int:
        c = (x - self.start_x) // self.piece_width
        r = (y - self.start_y) // self.piece_height
        c = max(0, min(self.cols - 1, int(c)))
        r = max(0, min(self.rows - 1, int(r)))
        return r * self.cols + c

    def get_coords_from_grid_pos(self, grid_pos: int) -> Tuple[float, float]:
        r = grid_pos // self.cols
        c = grid_pos % self.cols
        x = self.start_x + c * self.piece_width + (self.piece_width // 2)
        y = self.start_y + r * self.piece_height + (self.piece_height // 2)
        return x, y

    def is_originally_neighbor(self, idx1: int, idx2: int) -> bool:
        r1, c1 = idx1 // self.cols, idx1 % self.cols
        r2, c2 = idx2 // self.cols, idx2 % self.cols
        return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

    # def check_victory(self) -> bool:
    #     """모든 조각이 자기 정답 자리에 들어맞았는지 확인하고 값을 출력합니다."""
    #     for p in self.pieces:
    #         print(f"ID: {p.id} | 현재위치(current): {p.current_grid_pos} | 정답위치(correct): {p.correct_idx} | 일치여부: {p.current_grid_pos == p.correct_idx}")
        
    #     return all(p.current_grid_pos == p.correct_idx for p in self.pieces)
    
    def check_victory(self) -> bool:
        """모든 조각이 자기 자리에 일치하는지 검사합니다."""
        if not self.pieces:
            return False
        return all(p.is_correct for p in self.pieces)
