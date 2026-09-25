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

    def register_piece(self, piece: PuzzlePiece):
        self.pieces.append(piece)

    def get_piece_by_id(self, canvas_id: int) -> Optional[PuzzlePiece]:
        for p in self.pieces:
            if p.id == canvas_id:
                return p
        return None

    def get_grid_pos_from_coords(self, x: float, y: float) -> int:
        """픽셀 좌표를 3x3 칸 번호(0~8)로 변환합니다."""
        c = (x - self.start_x) // self.piece_width
        r = (y - self.start_y) // self.piece_height
        c = max(0, min(self.cols - 1, int(c)))
        r = max(0, min(self.rows - 1, int(r)))
        return r * self.cols + c

    def get_coords_from_grid_pos(self, grid_pos: int) -> Tuple[float, float]:
        """칸 번호(0~8)를 실제 캔버스 중심 좌표(x, y)로 변환합니다."""
        r = grid_pos // self.cols
        c = grid_pos % self.cols
        x = self.start_x + c * self.piece_width + (self.piece_width // 2)
        y = self.start_y + r * self.piece_height + (self.piece_height // 2)
        return x, y

    def is_originally_neighbor(self, idx1: int, idx2: int) -> bool:
        """원본 이미지 기준으로 두 조각이 상하좌우로 붙어있는 진짜 이웃인지 검증합니다."""
        r1, c1 = idx1 // self.cols, idx1 % self.cols
        r2, c2 = idx2 // self.cols, idx2 % self.cols
        return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

    def check_victory(self) -> bool:
        """모든 조각이 자기 정답 자리에 들어맞았는지 확인합니다."""
        return all(p.is_correct for p in self.pieces)
