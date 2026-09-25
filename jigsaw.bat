@echo off
chcp 65001

echo ===================================================
echo [1/3] 가상환경(.venv) 활성화 중...
echo ===================================================
call .venv\Scripts\activate

echo ===================================================
echo [2/3] PyInstaller 빌드 시작 (여러 줄 명령 실행)...
echo ===================================================
pyinstaller --onefile ^
--noconsole ^
--paths=. ^
--hidden-import=logging.handlers ^
--add-data "util;util" ^
--add-data "background.png;." ^
--add-data "player.png;." ^
--add-data "enemy.png;." ^
--add-data "gem.png;." ^
--add-data "gem_sound.wav;." ^
--add-data "gameover_sound.wav;." ^
game.py
pyinstaller --onefile --noconsole --paths=. ^
--hidden-import=logging.handlers ^
--add-data "util;util" ^
--add-data "./game/pic/images/puzzle.png;." ^
--add-data "./game/ddong/effect.wav;." ^
--add-data "./game/ddong/background2.mp3;." ^
./game/pic/jigsaw/jigsaw.py


echo ===================================================
echo [3/3] 빌드 완료! 아무 키나 누르면 창이 닫힙니다.
echo ===================================================
pause
