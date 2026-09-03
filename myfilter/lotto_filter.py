from abc import ABC, abstractmethod
from typing import List


# 1. 인터페이스
class LottoFilter(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def get_debug(self) -> bool: pass

    @property
    @abstractmethod
    def has_attr(self, attr_name: str) -> bool: pass

    @property
    @abstractmethod
    def get_min(self) -> int: pass

    @property
    @abstractmethod
    def get_max(self) -> int: pass

    @property
    @abstractmethod
    def get_bool_val(self) -> bool: pass

    @property
    @abstractmethod
    def description(self) -> str: pass

    @abstractmethod
    def filter(self, numbers: List[int]) -> bool: pass


class ALottoFilter(LottoFilter):
    def __init__(self, debug: bool=False):
        self.debug = debug

    def get_debug(self) -> bool:
        return self.debug

    def has_attr(self, attr_name: str) -> bool:
        return hasattr(self, attr_name)

    def get_min(self) -> int:
        if self.has_attr("min_val"):
            return self.min_val
        return -1

    def get_max(self) -> int:
        if self.has_attr("max_val"):
            return self.max_val
        return -1

    def get_bool_val(self) -> bool:
        if self.has_attr("bool_val"):
            return self.bool_val
        return False


# 2.1. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class ARangeFilter(ALottoFilter):
    def __init__(self, min_val: int, max_val: int, debug: bool=False):
        super().__init__(debug=debug)

        self.min_val = min_val
        self.max_val = max_val

    # def get_min(self) -> int:
    #     if self.has_attr("min_val"):
    #         return self.min_val
    #     return -1


    # def get_max(self) -> int:
    #     if self.has_attr("max_val"):
    #         return self.max_val
    #     return -1


    # def get_bool_val(self) -> bool:
    #     if self.has_attr("bool_val"):
    #         return self.bool_val
    #     return False


# 2.2. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class ABooleanFilter(ALottoFilter):
    def __init__(self, bool_val: bool, debug: bool=False):
        super().__init__(debug=debug)

        self.bool_val = bool_val

    # def get_debug(self) -> bool:
    #     return self.debug

    # def get_bool_val(self) -> bool:
    #     return self.bool_val


# 2.3. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class AMaxFilter(ALottoFilter):
    def __init__(self, max_val: int, debug: bool=False):
        super().__init__(debug=debug)

        self.max_val = max_val

    # def get_debug(self) -> bool:
    #     return self.debug

    # def get_max(self) -> int:
    #     if self.has_attr("max_val"):
    #         return self.max_val
    #     return -1

# 2.4. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class AMinFilter(ALottoFilter):
    def __init__(self, min_val: int, debug: bool=False):
        super().__init__(debug=debug)

        self.min_val = min_val

    # def get_debug(self) -> bool:
    #     return self.debug

    # def get_min(self) -> int:
    #     if self.has_attr("min_val"):
    #         return self.min_val
    #     return -1
