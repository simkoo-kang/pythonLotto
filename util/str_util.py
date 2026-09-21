import re


class Str:

    @staticmethod
    def strip_not_digit(s: str) -> str:
        return re.sub(r"\D", "", s)

    @staticmethod
    def number_format(number: int) -> str:
        return f"{number:,}"

    @staticmethod
    def get_class_name(clazz_object) -> str:
        return clazz_object.__class__.__name__


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    maxidx = 10
    stop = False
    if not stop:
        for a in range(maxidx):
            if a == 0:
                continue
            if stop:
                break
            for b in range(maxidx):
                if b == 0:
                    continue
                if stop:
                    break
                for c in range(maxidx):
                    if c == 0:
                        continue
                    plus = a + b + c
                    mult = a * b * c
                    if plus < mult:
                        continue
                    print(f"plus={plus}, mult={mult}")
                    if plus == mult:
                        print(f"(a,b,c) = ({a},{b},{c}) same")
                        # stop = True
                        # break
