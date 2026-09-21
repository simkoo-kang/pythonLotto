class Singleton:
    # 유일한 인스턴스를 저장할 클래스 변수
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # 인스턴스가 생성된 적이 없다면 새로 생성
            cls._instance = super().__new__(cls)
            print("create instance=======")

        print("__new__", args, kwargs)
        return cls._instance

    def __init__(self, teststr, testint, testintmore: int = 0):
        print(teststr, testint, testintmore)


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":

    s1 = Singleton("teststr", 5)
    s2 = Singleton("str", 10, 5)

    print(s1 is s2)
