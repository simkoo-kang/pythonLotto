from __future__ import annotations


class ListUtil:

    class StrBuilder:
        def __init__(self, def_var=None):
            self.sb = []
            if def_var is not None:
                self.sb.append(str(def_var))

        def append(self, pstr) -> ListUtil.StrBuilder:
            self.sb.append(str(pstr))
            return self

        def append_all(self, pvar) -> ListUtil.StrBuilder:
            """공백(스페이스 한 칸)을 추가합니다."""
            if (
                isinstance(pvar, list)
                or isinstance(pvar, tuple)
                or isinstance(pvar, set)
            ):
                for v in pvar:
                    self.sb.append(str(v))
            elif isinstance(pvar, dict):
                vals = pvar.values()
                for v in vals:
                    self.sb.append(str(v))
            else:
                self.sb.append(str(pvar))

            return self

        def append_line(self, pvar="") -> ListUtil.StrBuilder:
            """
            줄바꿈(\\n)을 추가합니다.
            문자열을 인자로 넣으면 문자열을 붙인 뒤 줄바꿈을 합니다.
            """
            if pvar:
                self.sb.append(str(pvar))
            self.sb.append("\n")
            return self

        def to_string(self, separator: str = "") -> str:
            """쌓인 모든 문자열을 하나로 합쳐서 반환합니다."""
            return separator.join(self.sb)

        def to_string_tab(self) -> str:
            """쌓인 모든 문자열을 하나로 합쳐서 반환합니다."""
            return "\t".join(self.sb)

    @staticmethod
    def contains(list1: list, list2: list) -> int:
        return len(set(list1) & set(list2))

    @staticmethod
    def join(list: list[int], separator: str = ",") -> str:
        return separator.join(map(str, list))


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    # 요청하신 예시 데이터 입력

    # yapf: disable
    a = [
        1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
    ]
    # yapf: enable
    print(ListUtil.join(a, ","))
