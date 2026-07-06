@echo off
REM 注册表添加脚本 - 实现开机自启动
REM 运行此脚本以将 DesktopUIToggle.ahk 添加到开机自启

setlocal enabledelayedexpansion

REM 获取脚本所在目录
set "ScriptPath=%~dp0DesktopUIToggle.ahk"
set "ScriptPath=!ScriptPath:\=/!"

REM 创建注册表条目
reg add "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "DesktopUIToggle" /t REG_SZ /d "\"C:\Program Files\AutoHotkey\AutoHotkey.exe\" \"%~dp0DesktopUIToggle.ahk\"" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 成功添加到开机自启
    echo ========================================
    echo 脚本路径: %~dp0DesktopUIToggle.ahk
    echo 注册表位置: HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    echo 项目名称: DesktopUIToggle
    echo.
    pause
) else (
    echo.
    echo 错误：无法添加到开机自启
    echo 请确保以管理员权限运行此脚本
    echo.
    pause
)

endlocal
