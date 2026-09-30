
from PIL import Image

# 1. 원본 고해상도 이미지 열기 (256x256 이상 권장)
img = Image.open("./movie/player256.png")

# 2. .ico 파일에 포함할 표준 크기들 지정
icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]

# 3. ico 포맷으로 저장 (sizes 옵션에 크기 배열 전달)
img.save("./movie/player.ico", format="ICO", sizes=icon_sizes)

print("멀티 사이즈 .ico 아이콘 변환 완료!")
