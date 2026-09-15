""" 
[예제] 나만의 미니 밴드 (pygame013.py)
"""
import pygame
pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("나만의 미니 밴드")

bg = pygame.image.load("./game/images/jigsaw/[ㄴ일]9151.mkv_002650870.png") # 배경 이미지 로드
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT)) # 배경 이미지 크기 조절

# 폰트 설정
font = pygame.font.SysFont("malgun gothic", 40)

# 배경음악 설정 및 재생 (무한 반복)
pygame.mixer.music.load("./game/sound/bgm1.mp3")
pygame.mixer.music.play(-1)

# ===== 1. 여기에 코드를 작성해주세요 =====
# 미션 1: 악기 개수만큼 pygame.mixer.Sound()를 사용하여 
# 각각 다른 변수(sound_piano, sound_drum, sound_guitar)에 효과음을 저장해 둡니다.
sound_piano = pygame.mixer.Sound("./game/sound/ddong/effect.wav")
sound_drom = pygame.mixer.Sound("./game/sound/ddong/collision.wav")
sound_guitar = pygame.mixer.Sound("./game/sound/pop.wav")

# 화면에 표시할 기본 메시지
current_play = "숫자키 1, 2, 3을 눌러보세요!"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 키보드를 눌렀을 때 악기 소리 재생
        if event.type == pygame.KEYDOWN:
            # ===== 2. 여기에 코드를 작성해주세요 =====
            # 미션 2: if-elif 문을 사용하여 숫자 1번(K_1), 2번(K_2), 3번(K_3) 키를 눌렀는지 파악합니다.
            # 미션 3: 각 키에 맞는 효과음 변수의 .play() 함수를 실행하고, current_play 변수의 글자를 알맞게 바꿔주세요. 
            if event.key == pygame.K_1:
                sound_piano.play()
                current_play = "피아노 연주 중!"
            elif event.key == pygame.K_2:
                sound_drom.play()
                current_play = "드럼 연주 중!"
            else:
                sound_guitar.play()
                current_play = "기타 연주 중!"

    # 화면 그리기
    screen.fill("lightyellow") 

    # 현재 연주 중인 악기 이름을 화면 중앙에 출력
    text_surface = font.render(current_play, True, "black")

    # 텍스트의 중심(center)을 화면의 중심(300, 200)에 맞추어 깔끔하게 배치합니다.
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

    pygame.display.update()

pygame.quit()