@echo off
REM ====================================================
REM Windows 11 DesktopUIToggle 故障排查脚本
REM 用于诊断和解决常见问题
REM ====================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo DesktopUIToggle 故障排查工具
echo ========================================
echo.

REM 检查 AutoHotkey 安装
echo [1/5] 检查 AutoHotkey 安装...
if exist "C:\Program Files\AutoHotkey\AutoHotkey.exe" (
    echo ✓ AutoHotkey 已安装
    "C:\Program Files\AutoHotkey\AutoHotkey.exe" /version
) else (
    echo ✗ 未找到 AutoHotkey 安装
    echo   请从 https://www.autohotkey.com/download/1.1/ 下载并安装
    echo.
    pause
    goto :eof
)

REM 检查脚本文件
echo.
echo [2/5] 检查脚本文件...
if exist "%~dp0DesktopUIToggle_Enhanced.ahk" (
    echo ✓ 找到 DesktopUIToggle_Enhanced.ahk
) else (
    echo ✗ 未找到 DesktopUIToggle_Enhanced.ahk
    echo   请确保脚本文件在同一目录中
)

REM 检查注册表中的启动项
echo.
echo [3/5] 检查开机自启动注册表项...
reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "DesktopUIToggle" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 找到开机自启动注册表项
    echo   注册表位置: HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    echo   项目名称: DesktopUIToggle
) else (
    echo - 未设置开机自启动（可以通过 SetupAutostart.bat 设置）
)

REM 检查 Windows 任务栏隐藏设置
echo.
echo [4/5] 检查 Windows 任务栏设置...
reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAutoHideInDesktopMode" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAutoHideInDesktopMode" ^| findstr TaskbarAutoHideInDesktopMode') do set TaskbarHide=%%i
    if !TaskbarHide! equ 1 (
        echo - 已启用任务栏自动隐藏
        echo   建议关闭此功能以获得更好的脚本体验
    ) else (
        echo ✓ 任务栏设置正确（自动隐藏已禁用）
    )
) else (
    echo ✓ 任务栏设置正确
)

REM 检查桌面图标设置
echo.
echo [5/5] 检查桌面图标设置...
cls
echo ========================================
echo 检查系统服务状态...
echo ========================================

tasklist /FI "IMAGENAME eq explorer.exe" /FO TABLE /NH | find /I "explorer.exe" >nul
if errorlevel 1 (
    echo ✗ Windows Explorer 未运行
    echo   这可能导致图标隐藏功能无法工作
) else (
    echo ✓ Windows Explorer 正常运行
)

echo.
echo ========================================
echo 故障排查完成
echo ========================================
echo.
echo 建议：
echo.
echo 如果三击没有反应：
echo   1. 尝试使用快捷键 Ctrl+Alt+H
echo   2. 确保鼠标三击时间间隔 < 200ms
echo.
echo 如果隐藏模式下任务栏未隐藏：
echo   1. 设置 → 个性化 → 任务栏
echo   2. 关闭"自动隐藏任务栏"选项
echo   3. 重新运行脚本
echo.
echo 如果恢复后图标未全部显示：
echo   1. 按 F5 刷新桌面
echo   2. 右键桌面 → 查看 → 勾选"显示桌面图标"
echo   3. 重新启动脚本
echo.

pause
