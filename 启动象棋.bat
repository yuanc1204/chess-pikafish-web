@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动象棋对弈服务...
start "" http://127.0.0.1:8899
python "%~dp0server.py"
pause
