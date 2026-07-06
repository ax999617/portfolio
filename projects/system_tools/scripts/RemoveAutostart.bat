@echo off
REM 删除开机自启注册表条目的脚本

setlocal enabledelayedexpansion

REM 删除注册表条目
reg delete "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "DesktopUIToggle" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 成功移除开机自启
    echo ========================================
    echo.
    pause
) else (
    echo.
    echo 提示：注册表条目不存在或已删除
    echo.
    pause
)

endlocal
