# group_manager.py
from typing import Set, List
from piece import PuzzlePiece

class GroupManager:
    def __init__(self):
        # 각 원소는 조각의 canvas_id를 담은 set입니다. 예: [{1}, {2}, {3}]
        self.groups: List[Set[int]] = []

    def initialize_groups(self, canvas_ids: List[int]):
        """모든 조각을 독립된 단독 그룹으로 초기화합니다."""
        self.groups = [{c_id} for c_id in canvas_ids]

    def get_group(self, canvas_id: int) -> Set[int]:
        """특정 조각이 속한 그룹 세트를 반환합니다."""
        for g in self.groups:
            if canvas_id in g:
                return g
        return {canvas_id}

    def merge_groups(self, id1: int, id2: int):
        """두 조각이 속한 그룹을 하나로 합칩니다 (딸깍 결합)."""
        g1 = self.get_group(id1)
        g2 = self.get_group(id2)
        
        if g1 != g2:
            self.groups.remove(g1)
            self.groups.remove(g2)
            self.groups.append(g1.union(g2))
