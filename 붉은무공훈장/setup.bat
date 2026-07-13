@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo pygame-ce 설치 중...
python -m pip install -r requirements.txt
echo.
echo 설치 완료. run.bat 으로 게임을 실행하세요.
pause
