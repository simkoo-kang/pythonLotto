import pygame
import random
import sys
import os

# 1. 게임 초기화 및 화면 설정
pygame.init()
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("장애물 피하기 게임 (최고 점수 저장)")

# FPS 설정
clock = pygame.time.Clock()

# 색상 정의 (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (120, 120, 120)
GOLD = (255, 215, 0)

# 폰트 설정
game_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 60)

# 게임 요소 기본 설정
player_size = 40
player_speed = 7
enemy_size = 30

# --- 파일에서 최고 점수 불러오기 함수 ---
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            try:
                return int(file.read())
            except ValueError:
                return 0
    return 0

# --- 파일에 최고 점수 저장하기 함수 ---
def save_high_score(new_high_score):
    with open("highscore.txt", "w") as file:
        file.write(str(new_high_score))

# 게임 리셋 함수
def reset_game():
    global player_x, player_y, obstacles, score, next_obstacle_score, base_enemy_speed, high_score
    player_x = (SCREEN_WIDTH / 2) - (player_size / 2)
    player_y = SCREEN_HEIGHT - player_size - 10
    score = 0
    base_enemy_speed = 5
    
    # 최고 점수 새로 불러오기
    high_score = load_high_score()
    
    # 초기 장애물 1개 생성
    obstacles = [{
        'x': random.randint(0, SCREEN_WIDTH - enemy_size),
        'y': 0,
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

    # [이벤트 처리]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 게임 오버 상태일 때 키 입력 처리
        if game_state == "GAMEOVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "PLAYING"
                elif event.key == pygame.K_q:
                    running = False

    # 3. 상태별 로직 및 화면 그리기
    if game_state == "PLAYING":
        score += 1

        # 점수가 일정 점수를 넘으면 장애물 추가
        if score >= next_obstacle_score:
            base_enemy_speed += 0.5
            obstacles.append({
                'x': random.randint(0, SCREEN_WIDTH - enemy_size),
                'y': 0,
                'speed': random.randint(4, 8)
            })
            next_obstacle_score += 200

        # 키 입력 조작
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        # 경계값 처리
        if player_x < 0:
            player_x = 0
        elif player_x > SCREEN_WIDTH - player_size:
            player_x = SCREEN_WIDTH - player_size

        # 플레이어 사각형
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        # 모든 장애물 위치 업데이트 및 충돌 검사
        for enemy in obstacles:
            enemy['y'] += enemy['speed']
            
            if enemy['y'] > SCREEN_HEIGHT:
                enemy['y'] = 0
                enemy['x'] = random.randint(0, SCREEN_WIDTH - enemy_size)
            
            # 충돌 감지
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_size, enemy_size)
            if player_rect.colliderect(enemy_rect):
                # 충돌한 순간 현재 점수가 최고 점수보다 높으면 파일에 저장
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = "GAMEOVER"

        # 그리기
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLUE, player_rect)
        
        for enemy in obstacles:
            pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'], enemy_size, enemy_size))
        
        # UI 표시
        score_text = game_font.render(f"Score: {score}", True, BLACK)
        high_score_text = game_font.render(f"Best: {high_score}", True, GOLD) # 최고 점수 노란색 표시
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
