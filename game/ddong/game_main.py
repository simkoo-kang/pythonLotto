import pygame
import random
import sys
import os

# 1. 게임 초기화 및 화면 설정
pygame.init()
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("장애물 피하기 게임 (이미지 적용)")

# FPS 설정
clock = pygame.time.Clock()

# 색상 정의 (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (120, 120, 120)
GOLD = (255, 215, 0)

# --- [추가] 사운드 재생을 위한 믹서 초기화 ---
pygame.mixer.init()

def load_sound(filename):
    try:
        return pygame.mixer.Sound(filename)
    except pygame.error:
        print(f"🔊 경고: {filename} 파일을 찾을 수 없어 소리가 나지 않습니다.")
        return None

# 효과음 파일 불러오기
gem_sound = load_sound("./game/ddong/effect.wav")
gameover_sound = load_sound("./game/ddong/collision.wav")

# 배경음악 파일 로드 및 무한 반복(-1) 재생
pygame.mixer.music.load("./game/ddong/background2.mp3")
pygame.mixer.music.play(-1) 

# 폰트 설정
game_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 60)

# --- [이미지 로드 및 크기 조절] ---
# 이미지가 없는 경우를 대비한 기본 이미지 생성 함수 (예외 처리)
def load_image(filename, size):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    except pygame.error:
        # 이미지가 없을 경우 대체할 컬러 서피스 생성
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if "player" in filename:
            surface.fill((0, 0, 255)) # 파란 네모
        else:
            surface.fill((255, 0, 0)) # 빨간 네모
        return surface

# 플레이어 및 장애물 이미지 불러오기 (원하는 크기로 강제 조정)
PLAYER_SIZE = (45, 55)
ENEMY_SIZE = (35, 35)

player_img = load_image("./game/ddong/man_img.png", PLAYER_SIZE)
enemy_img = load_image("./game/ddong/watermelon.png", ENEMY_SIZE)


# 보석 크기 및 이미지 로드 (없으면 녹색 네모로 대체)
GEM_SIZE = (30, 30)
try:
    gem_img = pygame.image.load("./game/ddong/banana.png").convert_alpha()
    gem_img = pygame.transform.scale(gem_img, GEM_SIZE)
except pygame.error:
    gem_img = pygame.Surface(GEM_SIZE, pygame.SRCALPHA)
    gem_img.fill((0, 255, 0)) # 녹색 네모

# 보석들을 담을 리스트와 타이머 변수
gems = []
gem_timer = 0


player_speed = 7

# --- 파일 입출력 함수 ---
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            try: return int(file.read())
            except ValueError: return 0
    return 0

def save_high_score(new_high_score):
    with open("highscore.txt", "w") as file:
        file.write(str(new_high_score))

# 게임 리셋 함수
def reset_game():
    global player_rect, obstacles, score, next_obstacle_score, base_enemy_speed, high_score
    global gems, gem_timer
    
    # 이미지의 기본 Rect를 가져와서 시작 위치 설정
    player_rect = player_img.get_rect()
    player_rect.centerx = SCREEN_WIDTH // 2
    player_rect.bottom = SCREEN_HEIGHT - 10
    
    score = 0
    base_enemy_speed = 5
    high_score = load_high_score()
    
    # 첫 장애물 생성 (위치 제어를 Rect 객체로 변경)
    first_enemy_rect = enemy_img.get_rect()
    first_enemy_rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0])
    first_enemy_rect.y = -ENEMY_SIZE[1]
    
    obstacles = [{
        'rect': first_enemy_rect,
        'speed': base_enemy_speed
    }]
    next_obstacle_score = 200
    
    gems = []
    gem_timer = 0

# 초기 설정
reset_game()
game_state = "PLAYING"

# 2. 게임 루프
running = True
while running:
    dt = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "GAMEOVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "PLAYING"
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False

    if game_state == "PLAYING":
        score += 1

        # 난이도 상승 (장애물 추가)
        if score >= next_obstacle_score:
            base_enemy_speed += 0.5
            new_enemy_rect = enemy_img.get_rect()
            new_enemy_rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0])
            new_enemy_rect.y = -ENEMY_SIZE[1]
            
            obstacles.append({
                'rect': new_enemy_rect,
                'speed': random.randint(4, 8)
            })
            next_obstacle_score += 200

        # 키 입력 및 플레이어 이동 (Rect 조작)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed

        # 경계값 처리
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > SCREEN_WIDTH:
            player_rect.right = SCREEN_WIDTH

        # --- [추가] 보석 주기적 생성 (약 3초마다) ---
        gem_timer += 1
        if gem_timer >= 90: 
            new_gem_rect = gem_img.get_rect()
            new_gem_rect.x = random.randint(0, SCREEN_WIDTH - GEM_SIZE[0])
            new_gem_rect.y = -GEM_SIZE[1]
            gems.append({
                'rect': new_gem_rect,
                'speed': 4 # 보석이 떨어지는 속도
            })
            gem_timer = 0

        # 장애물 이동 및 충돌 검사
        for enemy in obstacles:
            enemy['rect'].y += enemy['speed']
            
            # 바닥에 닿으면 위로 리셋
            if enemy['rect'].y > SCREEN_HEIGHT:
                enemy['rect'].y = -ENEMY_SIZE[1]
                enemy['rect'].x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0])
            
            # 충돌 감지 (Rect 객체끼리 바로 비교)
            if player_rect.colliderect(enemy['rect']):
                # --- [추가] 게임오버 효과음 재생 ---
                if gameover_sound:
                    gameover_sound.play()
                
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = "GAMEOVER"


        # --- [추가] 보석 이동 및 충돌 검사 ---
        for gem in gems[:]: # 복사본으로 반복문을 돌려 안전하게 삭제 가능하도록 함
            gem['rect'].y += gem['speed']
            
            # 플레이어가 보석을 먹었을 때
            if player_rect.colliderect(gem['rect']):
                # --- [추가] 보석 획득 효과음 재생 ---
                if gem_sound:
                    gem_sound.play()
                
                score += 500 # 500점 보너스!
                gems.remove(gem)
                
            # 바닥에 닿아 화면 밖으로 사라진 보석 제거
            if gem['rect'].y > SCREEN_HEIGHT:
                gems.remove(gem)

        # [화면 그리기]
        screen.fill(WHITE)
        
        # 사각형(draw.rect) 대신 이미지(blit) 그리기
        screen.blit(player_img, player_rect)
        for enemy in obstacles:
            screen.blit(enemy_img, enemy['rect'])
        
        # UI 표시
        score_text = game_font.render(f"Score: {score}", True, BLACK)
        high_score_text = game_font.render(f"Best: {high_score}", True, GOLD)
        count_text = game_font.render(f"Enemies: {len(obstacles)}", True, GRAY)
        
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 45))
        screen.blit(count_text, (SCREEN_WIDTH - 160, 10))

        # --- [추가] 생성된 모든 보석 그리기 ---
        for gem in gems:
            screen.blit(gem_img, gem['rect'])

    elif game_state == "GAMEOVER":
        screen.fill(BLACK)
        over_text = title_font.render("GAME OVER", True, RED)
        final_score_text = game_font.render(f"Final Score: {score}", True, WHITE)
        best_record_text = game_font.render(f"Highest Score: {high_score}", True, GOLD)
        retry_text = game_font.render("Press 'R' to Restart", True, GRAY)
        quit_text = game_font.render("Press 'Q' to Quit", True, GRAY)

        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 140))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 220))
        screen.blit(best_record_text, (SCREEN_WIDTH // 2 - best_record_text.get_width() // 2, 280))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, 420))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 480))

    pygame.display.update()

pygame.quit()
sys.exit()
