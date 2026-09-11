# piece.py
class PuzzlePiece:
    def __init__(self, canvas_id, image, correct_idx, initial_grid_pos):
        self.id = canvas_id
        self.image = image
        self.correct_idx = correct_idx
        self.current_grid_pos = initial_grid_pos

    @property
    def is_correct(self) -> bool:
        """이 조각이 정답 자리에 위치해 있는지 확인합니다."""
        return self.current_grid_pos == self.correct_idx
