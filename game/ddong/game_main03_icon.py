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
                elif event.key == pygame.K_q:
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
        if keys[keys[pygame.K_RIGHT]]:
            player_rect.x += player_speed

        # 경계값 처리
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > SCREEN_WIDTH:
            player_rect.right = SCREEN_WIDTH

        # 장애물 이동 및 충돌 검사
        for enemy in obstacles:
            enemy['rect'].y += enemy['speed']
            
            # 바닥에 닿으면 위로 리셋
            if enemy['rect'].y > SCREEN_HEIGHT:
                enemy['rect'].y = -ENEMY_SIZE[1]
                enemy['rect'].x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0])
            
            # 충돌 감지 (Rect 객체끼리 바로 비교)
            if player_rect.colliderect(enemy['rect']):
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = "GAMEOVER"

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
