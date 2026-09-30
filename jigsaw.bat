@echo off
chcp 65001

echo ===================================================
echo [1/3] 가상환경(.venv) 활성화 중...
echo ===================================================
:: "call .venv\Scripts\activate"

echo ===================================================
echo [2/3] PyInstaller 빌드 시작 (여러 줄 명령 실행)...
echo ===================================================

pyinstaller --noconfirm ^
--onefile ^
--windowed ^
--paths="." ^
--exclude-module="venv" ^
--exclude-module=".venv" ^
--add-data "game/pic/jigsaw/icon.ico;." ^
--icon="game/pic/jigsaw/icon.ico" ^
./game/pic/jigsaw/jigsaw.py

echo ===================================================
echo [3/3] 빌드 완료! 아무 키나 누르면 창이 닫힙니다.
echo ===================================================
pause
