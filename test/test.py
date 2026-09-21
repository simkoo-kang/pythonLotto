import copy
from pathlib import Path

lists = []
lists.append([0, 1])
lists.append([1, 1])
lists.append([2, 1])
lists.append([3, 1])

if [0, 1] in lists:
    print("exist")
else:
    print("not exist")


if (0, 1) in lists:
    print("exist")
else:
    print("not exist")

lists.sort()
print(lists)

copys = lists.copy()
deeps = copy.deepcopy(lists)

copys.reverse()
print(lists)
print(copys)
print(deeps)

print(__file__)


# 예시 파일 경로
file_path_str = r"D:\Workspace\vscode\lotto\game\sokoban\sokoban.py"

# Path 객체 생성
path = Path(file_path_str)

# 각각의 요소 추출
folder_path = path.parent  # 폴더 경로
file_name = path.stem  # 확장자를 제외한 파일 이름
file_ext = path.suffix  # 확장자 (점 '.' 포함)
full_name = path.name  # 확장자를 포함한 전체 파일명

# 출력 결과
print(f"폴더 경로: {folder_path}")  # D:\Workspace\vscode\lotto\game\sokoban
print(f"파일 이름: {file_name}")  # sokoban
print(f"확 장 자 : {file_ext}")  # .py
print(f"전체 파일명: {full_name}")  # sokoban.py

x, a1, b1 = 0, 1, 1
while x < 30:
    a, b = x**9, 3**x
    print("x=", x, a, b, (b - b1) / (a - a1))
    if a == b:
        break
    x += 1
    a1 = a
    b1 = b
