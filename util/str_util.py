
class Str:

    @staticmethod    
    def number_format(number: int) -> str:
        return f"{number:,}"


    @staticmethod    
    def get_class_name(clazz_object) -> str:
        return clazz_object.__class__.__name__


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    # 요청하신 예시 데이터 입력
    a = [1, 2, 3, 4, 5, 6]
    b = [5,6,7,8,9,0]
    c=a+b
    d = sorted(list(set(c)))
    print(c, d)

    print(0,3,a[0:3])
    print(1,3,a[1:3])
    print(0,12,c[0:12])
    print(0,12,c[:12])
    print(len(c),c[0:12])
