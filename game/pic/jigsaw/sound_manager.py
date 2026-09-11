# sound_manager.py
import sys
import os
import pygame

# 가상환경 및 PyInstaller 경로 변환 함수 정의
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 사운드 객체를 담아둘 글로벌 변수 초기화
sound_effect = None

def init_sounds():
    """메인 루프 시작 전 사운드를 단 한 번 초기화하는 함수"""
    global sound_effect
    
    # 믹서가 초기화되지 않았다면 초기화
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    try:
        sound_effect = pygame.mixer.Sound(resource_path("./game/ddong/effect.wav"))
    except Exception:
        sound_effect = None

def effect_play():
    if sound_effect:
        sound_effect.play()
