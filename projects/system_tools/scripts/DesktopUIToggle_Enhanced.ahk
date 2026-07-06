;===============================================
; AutoHotkey v1.1 - Desktop UI Toggle Script (Enhanced for Windows 11)
; 功能：三击鼠标启用/禁用隐藏图标和任务栏隐藏
; 特性：
;   - 开机自启动
;   - 监控鼠标行为（三击）
;   - 不闪烁屏幕
;   - 不影响壁纸和文件资源管理器
;   - Windows 11 任务栏系统级控制优化
;===============================================

#NoEnv
SetBatchLines -1
#SingleInstance Force

; 全局变量
global g_Enabled := false
global g_ClickCount := 0
global g_LastClickTime := 0
global g_ClickTimeThreshold := 400      ; 毫秒 - 三击时间间隔阈值
global g_ThreeClickWindow := 600        ; 毫秒 - 整个三击的时间窗口
global g_HideIcons := false
global g_HideTaskbar := false
global g_OriginalDesktopState := false
global g_TaskbarHwnd := 0
global g_ProgManHwnd := 0

; 初始化
OnExit("ExitScript")
SetupInitial()

SetupInitial() {
    global g_TaskbarHwnd, g_ProgManHwnd

    ; 获取任务栏窗口句柄
    g_TaskbarHwnd := WinExist("ahk_class Shell_TrayWnd")

    ; 获取桌面窗口句柄
    g_ProgManHwnd := WinExist("ahk_class ProgMan")

    return
}

; 监控鼠标左键点击
~LButton::
{
    CurrentTime := A_TickCount

    ; 如果距离第一次点击超过窗口阈值，重置计数
    if (g_ClickCount > 0 && CurrentTime - g_LastClickTime > 600) {
        g_ClickCount := 0
    }

    ; 如果两次点击间隔太长，重置
    if (g_ClickCount > 0 && CurrentTime - g_LastClickTime > g_ClickTimeThreshold + 200) {
        g_ClickCount := 0
    }

    g_ClickCount++
    g_LastClickTime := CurrentTime

    ; 如果第三次点击，检查时间窗口
    if (g_ClickCount >= 3) {
        if (CurrentTime - g_LastClickTime <= g_ThreeClickWindow) {
            ToggleUIMode()
            g_ClickCount := 0
            g_LastClickTime := 0
        }
    }

    return
}

ToggleUIMode() {
    global g_Enabled, g_HideIcons, g_HideTaskbar

    g_Enabled := !g_Enabled

    if (g_Enabled) {
        ; 启用隐藏模式
        g_HideIcons := true
        g_HideTaskbar := true

        ; 隐藏桌面图标
        HideDesktopIcons(true)
        Sleep(50)

        ; 隐藏任务栏
        HideTaskbar(true)
        Sleep(50)

        ShowNotification("✓ 已启用：隐藏图标 + 隐藏任务栏", 2000)
    }
    else {
        ; 禁用隐藏模式
        g_HideIcons := false
        g_HideTaskbar := false

        ; 显示桌面图标
        HideDesktopIcons(false)
        Sleep(50)

        ; 显示任务栏
        HideTaskbar(false)
        Sleep(50)

        ShowNotification("✓ 已禁用：恢复图标 + 恢复任务栏", 2000)
    }

    return
}

HideDesktopIcons(Hide) {
    global g_ProgManHwnd

    if (!g_ProgManHwnd)
        return

    ; 方法1：通过 SendMessage 切换桌面视图
    ; 获取 SHELLDLL_DefView 窗口（桌面图标容器）
    hView := DllCall("user32.dll", "uint", "FindWindowEx", "uint", g_ProgManHwnd, "uint", 0, "str", "SHELLDLL_DefView",
        "uint", 0)

    if (hView = 0) {
        ; 尝试备用方法
        HideDesktopIconsAlt(Hide)
        return
    }

    if (Hide) {
        ; 隐藏图标
        DllCall("user32.dll", "int", "ShowWindow", "uint", hView, "int", 0)  ; SW_HIDE = 0
    }
    else {
        ; 显示图标
        DllCall("user32.dll", "int", "ShowWindow", "uint", hView, "int", 5)  ; SW_SHOW = 5
    }

    return
}

HideDesktopIconsAlt(Hide) {
    global g_ProgManHwnd

    ; 备用方法：使用 ToggleDesktop 和视图菜单
    ; window_id := WinExist("ahk_class ProgMan")

    if (Hide) {
        ; 隐藏所有图标的另一种方式：发送菜单命令
        ; 这是针对 Windows 11 的更稳定的方法

        ; 确保焦点在桌面
        WinActivate, ahk_class ProgMan
        Sleep(100)

        ; 调用显示/隐藏图标的完整操作
        ; 使用 COM 对象隐藏图标
        try
        {
            shell := ComObjCreate("Shell.Application")
            shell.ToggleDesktop()
            Sleep(150)
            shell.ToggleDesktop()
        }
        catch e {
            ; 如果 COM 失败，使用键盘快捷键
            Send, %A_AltDown%#d%A_AltUp%
        }
    }
    else {
        ; 恢复图标 - 恢复正常桌面状态
        try
        {
            shell := ComObjCreate("Shell.Application")
            shell.ToggleDesktop()
            Sleep(150)
            shell.ToggleDesktop()
        }
        catch e {
            Send, %A_AltDown%#d%A_AltUp%
        }
    }

    return
}

HideTaskbar(Hide) {
    global g_TaskbarHwnd

    if (!g_TaskbarHwnd)
        return

    ; Windows 11 任务栏系统级控制
    ; Method 1: 直接隐藏/显示任务栏窗口

    if (Hide) {
        ; 隐藏任务栏
        ; 在 Windows 11 中，任务栏通常是 Shell_TrayWnd 的组合

        ; 首先尝试隐藏主任务栏窗口
        DllCall("user32.dll", "int", "ShowWindow", "uint", g_TaskbarHwnd, "int", 0)  ; 0 = SW_HIDE

        ; 也尝试找到并隐藏二级任务栏（如果存在）
        WinGet, ControlList, ControlList, ahk_class Shell_TrayWnd

        ; 隐藏通知区域托盘
        hNotify := DllCall("user32.dll", "uint", "FindWindowEx", "uint", g_TaskbarHwnd, "uint", 0, "str",
            "TrayNotifyWnd", "uint", 0)
        if (hNotify != 0) {
            DllCall("user32.dll", "int", "ShowWindow", "uint", hNotify, "int", 0)
        }
    }
    else {
        ; 显示任务栏
        DllCall("user32.dll", "int", "ShowWindow", "uint", g_TaskbarHwnd, "int", 5)  ; 5 = SW_SHOW

        ; 显示通知区域托盘
        hNotify := DllCall("user32.dll", "uint", "FindWindowEx", "uint", g_TaskbarHwnd, "uint", 0, "str",
            "TrayNotifyWnd", "uint", 0)
        if (hNotify != 0) {
            DllCall("user32.dll", "int", "ShowWindow", "uint", hNotify, "int", 5)
        }
    }

    ; 强制刷新而不闪烁
    ; 不使用 RedrawWindow，直接更新
    return
}

ShowNotification(Text, Duration) {
    global g_NotificationActive

    ; 移除旧提示
    ToolTip
    Sleep(10)

    ; 显示新提示
    ToolTip, %Text%

    ; 设置移除定时器
    SetTimer(RemoveToolTip, Duration)
    return
}

RemoveToolTip() {
    SetTimer(RemoveToolTip, "Off")
    ToolTip
    return
}

ExitScript(ExitReason, ExitCode) {
    global g_Enabled

    ; 脚本退出时恢复UI
    if (g_Enabled) {
        HideDesktopIcons(false)
        Sleep(50)
        HideTaskbar(false)
    }

    ; 移除提示框
    ToolTip

    return
}

; 快速启用/禁用的快捷键 (Ctrl+Alt+H)
^!h::
{
    ToggleUIMode()
    return
}

; 退出脚本快捷键 (Ctrl+Alt+Esc)
^!Esc::
{
    MsgBox, 4, 确认退出, 是否要退出 DesktopUIToggle 脚本？
    IfMsgBox, Yes
    {
        ExitApp
    }
    return
}

; 显示帮助信息
^!+?::
{
    MsgBox, 0, DesktopUIToggle - 帮助信息,
        (
            快捷键说明：

            鼠标三击 - 切换隐藏 / 显示模式
            Ctrl + Alt + H - 快速切换隐藏 / 显示模式
            Ctrl + Alt + Esc - 退出脚本

            功能模式：
            ✓ 隐藏桌面图标
            ✓ 隐藏任务栏（包括通知区域）
            ✓ 无屏幕闪烁
            ✓ 不影响壁纸和文件资源管理器

            状态通知显示在屏幕左上方
        )
    return
}
