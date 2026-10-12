@echo off
rem ============================================================
rem  Trae2api-cn 授权助手（通用版）
rem  中转站:   http://127.0.0.1:8000
rem  本机回调: http://127.0.0.1:8765/authorize
rem  生成时间: 自动生成
rem  本机默认部署的通用版；其他部署请从控制台下载助手。
rem ============================================================
setlocal enableextensions disabledelayedexpansion
chcp 65001 >nul
set "RELAY=http://127.0.0.1:8000"
set "PORT=8765"
set "HELPER=%~dp0web_login.py"
set "TMP_HELPER=%HELPER%.download-%RANDOM%"

if not exist "%HELPER%" (
  echo [1/2] 正在从中转站下载授权助手脚本 web_login.py ...
  del /q "%TMP_HELPER%" >nul 2>nul
  curl -fsSL --max-time 20 -o "%TMP_HELPER%" "%RELAY%/web/login/download?as=py"
  if not errorlevel 1 move /y "%TMP_HELPER%" "%HELPER%" >nul
  del /q "%TMP_HELPER%" >nul 2>nul
)
if not exist "%HELPER%" (
  echo 未取到 web_login.py，请在中转站页面点“授权助手 web_login.py”下载到本目录后重试。
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  where py >nul 2>nul
  if errorlevel 1 (
    echo 未检测到 Python 3，请先安装 Python 并勾选 Add to PATH。
    pause
    exit /b 1
  )
  set "PYCMD=py -3"
) else (
  set "PYCMD=python"
)

echo [2/2] 启动本机授权监听器: http://127.0.0.1:%PORT%
echo 浏览器会自动打开中转站授权页面，在该页面点击授权登录即可。
%PYCMD% "%HELPER%" --relay "%RELAY%" --port "%PORT%"
if errorlevel 1 (
  echo 启动失败，请确认已安装 Python 3 并加入 PATH。
  pause
  exit /b 1
)
