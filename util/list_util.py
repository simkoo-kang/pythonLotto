

class ListUtil:
    
    @staticmethod    
    def contains(list1: list, list2: list) -> int:
        return len(set(list1) & set(list2))

    @staticmethod    
    def join(list: list[int], separator: str=",") -> str:
        return separator.join(map(str, list))


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    # 요청하신 예시 데이터 입력
    a = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]
    print(ListUtil.join(a, ","))
    