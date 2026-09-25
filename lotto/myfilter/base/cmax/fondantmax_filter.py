from typing import List

import util.lotto_util as lotto_util
from lotto.myfilter.lotto_filter import AMaxFilter, LottoFilter


class FondantMaxFilter(AMaxFilter):
    """_summary_
    # 퐁당퐁당 패턴 
    max_count: int = 13
    Args:
        AMaxFilter (_type_): _description_
    Returns:
        _type_: _description_
    """

    max_count: int = 13

    def __init__(self, max_val: int = 6, index: int = 0, optional: bool=True, debug: bool=False):
        super().__init__(max_val=max_val, optional=optional, debug=debug)

        match index:
            case 0:
                self.sub_filter = FondantMax01Filter(max_val=max_val)
            case 1:
                self.sub_filter = FondantMax02Filter(max_val=max_val)
            case 2:
                self.sub_filter = FondantMax03Filter(max_val=max_val)
            case 3:
                self.sub_filter = FondantMax04Filter(max_val=max_val)
            case 4:
                self.sub_filter = FondantMax05Filter(max_val=max_val)
            case 5:
                self.sub_filter = FondantMax06Filter(max_val=max_val)
            case 6:
                self.sub_filter = FondantMax07Filter(max_val=max_val)
            case 7:
                self.sub_filter = FondantMax08Filter(max_val=max_val)
            case 8:
                self.sub_filter = FondantMax09Filter(max_val=max_val)
            case 9:
                self.sub_filter = FondantMax10Filter(max_val=max_val)
            case 10:
                self.sub_filter = FondantMax11Filter(max_val=max_val)
            case 11:
                self.sub_filter = FondantMax12Filter(max_val=max_val)
            case 12:
                self.sub_filter = FondantMax13Filter(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max01 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        if not self.sub_filter.filter(numbers):
            if self.debug:
                print("False :", self.sub_filter.__class__.__name__)
            return False
        return True


# 퐁당퐁당 패턴 - 세로 라인 1,2,4,5
class FondantMax01Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 라인 1,2,4,5
    fondants = [ 1, 2, 4, 5, 8, 9, 11, 12, 15, 16, 18, 19, 22, 23, 25, 26, 29, 30, 32, 33, 36, 37, 39, 40, 43, 44 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max01 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 세로 라인 3,4,6,7
class FondantMax02Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 라인 3,4,6,7
    fondants = [ 3, 4, 6, 7, 10, 11, 13, 14, 17, 18, 20, 21, 24, 25, 27, 28, 31, 32, 34, 35, 38, 39, 41, 42, 45 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max02 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 좌우 2줄 패턴
class FondantMax03Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 좌우 2줄 패턴
    fondants = [ 1, 2, 6, 7, 8, 9, 13, 14, 15, 16, 20, 21, 22, 23, 27, 28, 29, 30, 34, 35, 36, 37, 41, 42, 43, 44 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max03 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 가로 세줄 패턴 01
class FondantMax04Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 가로 세줄 패턴 01
    fondants = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max04 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 가로 세줄 패턴 02
class FondantMax05Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 가로 세줄 패턴 02
    fondants = [ 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max05 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 가로 세줄 패턴 03
class FondantMax06Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 가로 세줄 패턴 03
    fondants = [ 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max06 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 가로 세줄 패턴 04
class FondantMax07Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 가로 세줄 패턴 04
    fondants = [ 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 47, 38, 39, 40, 41, 42 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max07 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 가로 세줄 패턴 05
class FondantMax08Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 가로 세줄 패턴 05
    fondants = [ 29, 30, 31, 32, 33, 34, 35, 36, 47, 38, 39, 40, 41, 42, 43, 44, 45 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max08 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 세로 세줄 패턴 01
class FondantMax09Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 세줄 패턴 01
    fondants = [ 1, 2, 3, 8, 9, 10, 15, 16, 17, 22, 23, 24, 29, 30, 31, 36, 37, 38, 43, 44, 45 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max09 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 세로 세줄 패턴 02
class FondantMax10Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 세줄 패턴 02
    fondants = [ 2, 3, 4, 9, 10, 11, 16, 17, 18, 23, 24, 25, 30, 31, 32, 37, 38, 39, 44, 45 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max10 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 세로 세줄 패턴 03
class FondantMax11Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 세줄 패턴 03
    fondants = [ 3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26, 31, 32, 33, 38, 39, 40, 45 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max11 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 세로 세줄 패턴 04
class FondantMax12Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 세줄 패턴 04
    fondants = [ 4, 5, 6, 11, 12, 13, 18, 19, 20, 25, 26, 27, 32, 33, 34, 39, 40, 41 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max12 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)


# 퐁당퐁당 패턴 - 세로 세줄 패턴 05
class FondantMax13Filter(AMaxFilter):

    # 퐁당퐁당 패턴 - 세로 세줄 패턴 05
    fondants = [ 5, 6, 7, 12, 13, 14, 19, 20, 21, 26, 27, 28, 33, 34, 35, 40, 41, 42 ]

    def __init__(self, max_val: int = 6):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Fondant Max13 Filter"

    @property
    def description(self) -> str: return f"일치하는 번호가 {self.max_val}와 같은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return not self.max_val == lotto_util.get_match_count_with_target_list(numbers, self.fondants)

