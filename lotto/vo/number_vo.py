class NumberVO:
    def __init__(
        self, round: int = 0, date: str = "", numbers: list = None, bonus: int = None
    ):
        self.round = round  # 회차
        self.date = date
        self.numbers = sorted(numbers) if numbers else []  # 메인 번호 6개
        self.bonus = bonus  # 보너스 번호

    def copyOf(self):
        return NumberVO(
            round=self.round,
            date=self.date,
            numbers=self.numbers.copy(),
            bonus=self.bonus,
        )

    def get_round(self) -> int:
        return self.round

    def set_round(self, round: int):
        self.round = round

    def get_date(self) -> str:
        return self.date

    def set_date(self, date: str):
        self.date = date

    def get_numbers(self) -> list:
        return self.numbers

    def set_numbers(self, numbers: list):
        self.numbers = sorted(numbers)

    def get_bonus(self) -> int:
        return self.bonus

    def set_bonus(self, bonus: int):
        self.bonus = bonus

    def toString(self, isSum: bool = False, isBonus: bool = False) -> str:
        """객체 상태를 문자열로 반환 (디버깅용)"""
        str = "-".join(f"{num:02d}" for num in self.numbers[:6])
        if isBonus and self.bonus is not None:
            str += f"\t{self.bonus:02d}]"
        if isSum:
            str += f"\t{sum(self.numbers)}"

        return str
