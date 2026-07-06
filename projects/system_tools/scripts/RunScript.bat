@echo off
REM ====================================================
REM 直接启动 DesktopUIToggle 脚本
REM 双击此文件快速启动脚本
REM ====================================================

setlocal enabledelayedexpansion

REM 获取当前脚本所在目录
set "ScriptDir=%~dp0"

REM 检查增强版脚本是否存在
if not exist "%ScriptDir%DesktopUIToggle_Enhanced.ahk" (
    echo 错误: 找不到 DesktopUIToggle_Enhanced.ahk
    echo 请确保此文件与 RunScript.bat 在同一目录
    pause
    exit /b 1
)

REM 检查 AutoHotkey 是否已安装
if not exist "C:\Program Files\AutoHotkey\AutoHotkey.exe" (
    echo 错误: AutoHotkey 未安装或安装位置不正确
    echo.
    echo 请从以下地址下载安装 AutoHotkey v1.1:
    echo https://www.autohotkey.com/download/1.1/
    echo.
    echo 安装时请选择标准安装位置: C:\Program Files\AutoHotkey\
    echo.
    pause
    exit /b 1
)

REM 启动脚本
echo 启动 DesktopUIToggle...
"C:\Program Files\AutoHotkey\AutoHotkey.exe" "%ScriptDir%DesktopUIToggle_Enhanced.ahk"

REM 如果脚本因某种原因退出，显示消息
echo.
echo 脚本已停止运行
pause
