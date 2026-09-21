import calendar
from datetime import datetime, timedelta


class CDate:

    DASH_DATE_FORMAT = "%Y-%m-%d"
    """_summary_
    # default '-' format 2026-09-20
    """

    def __init__(self, date_str: str = None, fmt: str = "%Y-%m-%d"):
        """
        초기화 메서드.
        date_str을 지정하지 않으면 자동으로 '오늘 날짜'로 설정됩니다.
        """
        self.fmt = fmt
        if date_str:
            # 다양한 기호(., -, /)에 대응하기 위해 하이픈(-)으로 통일 후 파싱
            clean_str = date_str.replace(".", "-").replace("/", "-")
            self.dt = datetime.strptime(clean_str, self.fmt)
        else:
            self.dt = datetime.now()

    def add_days(self, days: int) -> "CDate":
        """지정한 일수만큼 날짜를 더합니다. (음수를 넣으면 뺍니다)"""
        self.dt += timedelta(days=days)
        return self  # 체이닝을 위해 자기 자신 반환

    def sub_days(self, days: int) -> "CDate":
        """지정한 일수만큼 날짜를 뺍니다."""
        self.dt -= timedelta(days=days)
        return self

    def get_dday(self, target_date_str: str) -> int:
        """다른 날짜와의 차이(D-Day)를 계산하여 일수(int)로 반환합니다."""
        clean_str = target_date_str.replace(".", "-").replace("/", "-")
        target_dt = datetime.strptime(clean_str, self.fmt)
        # (대상 날짜 - 현재 설정된 날짜)
        return (target_dt - self.dt).days

    def get_week(self) -> int:
        """_summary_
        Returns:
            int: _description_ 0[월], 1[화], ... 6[일]
        """
        return self.dt.weekday()

    def get_weekday_kr(self, is_full_name: bool = False) -> str:
        """
        현재 설정된 날짜의 요일을 한국어로 반환합니다.
        - is_full_name=True 이면 '일요일(6)', '월요일(0)' 형식으로 반환합니다.
        - 기본값(False)은 '일', '월' 형식으로 반환합니다.
        """
        # weekday()는 월요일(0) ~ 일요일(6)을 반환하므로 순서에 맞게 리스트 정의
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]

        weekday_name = weekdays[self.dt.weekday()]

        return f"{weekday_name}요일" if is_full_name else weekday_name

    def get_weekday_en(self, is_full_name: bool = False) -> str:
        """
        현재 설정된 날짜의 요일을 영문으로 반환합니다.
        - is_full_name=True 이면 'Sunday(6)', 'Monday(0)' 형식으로 반환합니다.
        - 기본값(False)은 'Sun', 'Mon' 형식으로 반환합니다.
        """
        # weekday()는 월요일(0) ~ 일요일(6)을 반환하므로 순서에 맞게 리스트 정의
        # weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return (
            datetime.now().strftime("%A")
            if is_full_name
            else datetime.now().strftime("%a")
        )

    def is_after(self, target_date_str: str) -> bool:
        """현재 날짜가 대상 날짜보다 '이후(더 미래)'인지 확인합니다."""
        clean_str = target_date_str.replace(".", "-").replace("/", "-")
        target_dt = datetime.strptime(clean_str, self.fmt)
        return self.dt > target_dt

    def is_before(self, target_date_str: str) -> bool:
        """현재 날짜가 대상 날짜보다 '이전(더 과거)'인지 확인합니다."""
        clean_str = target_date_str.replace(".", "-").replace("/", "-")
        target_dt = datetime.strptime(clean_str, self.fmt)
        return self.dt < target_dt

    def is_equal(self, target_date_str: str) -> bool:
        """두 날짜가 '같은 날짜'인지 확인합니다."""
        clean_str = target_date_str.replace(".", "-").replace("/", "-")
        target_dt = datetime.strptime(clean_str, self.fmt)
        return self.dt == target_dt

    def add_months(self, months: int) -> "CDate":
        """지정한 개월 수만큼 날짜를 더합니다. (음수 가능)"""
        # 현재 연도와 월에 개월 수를 더해 새로운 연/월 계산
        month = self.dt.month - 1 + months
        year = self.dt.year + month // 12
        month = month % 12 + 1

        # 만약 1월 31일에서 1개월을 더할 때, 2월 31일은 없으므로 2월의 말일로 조정합니다.
        day = min(self.dt.day, calendar.monthrange(year, month)[1])

        self.dt = datetime(
            year, month, day, self.dt.hour, self.dt.minute, self.dt.second
        )
        return self

    def add_years(self, years: int) -> "CDate":
        """지정한 연도 수만큼 날짜를 더합니다. (음수 가능)"""
        year = self.dt.year + years
        month = self.dt.month

        # 윤년 2월 29일에서 평년으로 넘어갈 때 예외 처리 (2월 28일로 변경)
        day = min(self.dt.day, calendar.monthrange(year, month)[1])

        self.dt = datetime(
            year, month, day, self.dt.hour, self.dt.minute, self.dt.second
        )
        return self

    def last_day_of_month(self) -> "CDate":
        """현재 설정된 달의 마지막 날짜(말일)로 강제 변경합니다."""
        # calendar.monthrange(연도, 월) -> (시작요일, 해당 월의 총 일수) 반환
        _, last_day = calendar.monthrange(self.dt.year, self.dt.month)
        self.dt = self.dt.replace(day=last_day)
        return self

    def to_string(self, custom_fmt: str = None) -> str:
        """원하는 형식의 문자열(YYYY-MM-DD 등)로 출력합니다."""
        return self.dt.strftime(custom_fmt if custom_fmt else self.fmt)
