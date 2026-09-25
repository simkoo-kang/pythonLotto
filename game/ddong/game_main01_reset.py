import pygame
import random
import sys

# 1. 게임 초기화 및 화면 설정
pygame.init()
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("장애물 피하기 게임 (난이도 상승)")

# FPS 설정
clock = pygame.time.Clock()

# 색상 정의 (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (120, 120, 120)

# 폰트 설정
game_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 60)

# 게임 요소 기본 설정
player_size = 40
player_speed = 7
enemy_size = 30

# 게임 리셋 함수
def reset_game():
    global player_x, player_y, obstacles, score, next_obstacle_score, base_enemy_speed
    player_x = (SCREEN_WIDTH / 2) - (player_size / 2)
    player_y = SCREEN_HEIGHT - player_size - 10
    score = 0
    base_enemy_speed = 5
    
    # 초기 장애물 1개 생성 (x좌표, y좌표, 속도)
    obstacles = [{
        'x': random.randint(0, SCREEN_WIDTH - enemy_size),
        'y': 0,
        'speed': base_enemy_speed
    }]
    # 다음 장애물이 추가되는 점수 기준
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
                elif event.key == pygame.K_q or pygame.K_ESCAPE:
                    running = False

    # 3. 상태별 로직 및 화면 그리기
    if game_state == "PLAYING":
        score += 1

        # 점수가 일정 점수(next_obstacle_score)를 넘으면 장애물 추가
        if score >= next_obstacle_score:
            base_enemy_speed += 0.5 # 전체적인 기본 속도도 약간 증가
            obstacles.append({
                'x': random.randint(0, SCREEN_WIDTH - enemy_size),
                'y': 0,
                'speed': random.randint(4, 8) # 장애물마다 약간 다른 속도 부여
            })
            next_obstacle_score += 200 # 다음 추가 기준 점수 갱신 (200점마다 추가)

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
            
            # 장애물이 바닥에 닿으면 위로 리셋
            if enemy['y'] > SCREEN_HEIGHT:
                enemy['y'] = 0
                enemy['x'] = random.randint(0, SCREEN_WIDTH - enemy_size)
            
            # 충돌 감지
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy_size, enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_state = "GAMEOVER"

        # 그리기
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLUE, player_rect)
        
        # 리스트에 있는 모든 장애물 그리기
        for enemy in obstacles:
            pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'], enemy_size, enemy_size))
        
        score_text = game_font.render(f"Score: {score}", True, BLACK)
        # 현재 장애물 개수도 화면에 표시
        count_text = game_font.render(f"Enemies: {len(obstacles)}", True, GRAY)
        
        screen.blit(score_text, (10, 10))
        screen.blit(count_text, (10, 45))

    elif game_state == "GAMEOVER":
        screen.fill(BLACK)
        over_text = title_font.render("GAME OVER", True, RED)
        final_score_text = game_font.render(f"Final Score: {score}", True, WHITE)
        retry_text = game_font.render("Press 'R' to Restart", True, GRAY)
        quit_text = game_font.render("Press 'Q' to Quit", True, GRAY)

        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 180))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 260))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, 400))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 460))

    pygame.display.update()

pygame.quit()
sys.exit()
