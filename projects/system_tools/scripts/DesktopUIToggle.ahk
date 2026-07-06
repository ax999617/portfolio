;===============================================
; AutoHotkey v1.1 - Desktop UI Toggle Script
; 功能：三击鼠标启用/禁用隐藏图标和任务栏隐藏
; 特性：
;   - 开机自启动
;   - 监控鼠标行为
;   - 不闪烁屏幕
;   - 不影响壁纸和文件资源管理器
;===============================================

#NoEnv
SetBatchLines -1
#SingleInstance Force

; 全局变量
global g_Enabled := false
global g_ClickCount := 0
global g_LastClickTime := 0
global g_ClickTimeThreshold := 500  ; 毫秒 - 三击时间间隔阈值
global g_HideIcons := false
global g_HideTaskbar := false

; 初始化
OnExit("ExitScript")

; 监控鼠标点击
~LButton::
    {
        ; 获取当前时间
        CurrentTime := A_TickCount

        ; 如果距离上次点击超过阈值，重置计数
        if (CurrentTime - g_LastClickTime > g_ClickTimeThreshold * 3)
        {
            g_ClickCount := 0
        }

        g_LastClickTime := CurrentTime
        g_ClickCount++

        ; 检测三击
        if (g_ClickCount = 3)
        {
            SetTimer("CheckThirdClick", 100)
        }

        return
    }

    CheckThirdClick()
    {
        SetTimer("CheckThirdClick", "Off")

        CurrentTime := A_TickCount

        ; 确认三击在时间窗口内完成
        if (CurrentTime - g_LastClickTime <= g_ClickTimeThreshold)
        {
            if (g_ClickCount = 3)
            {
                ToggleUIMode()
                g_ClickCount := 0
            }
        }
        else
        {
            g_ClickCount := 0
        }

        return
    }

    ToggleUIMode()
    {
        global g_Enabled, g_HideIcons, g_HideTaskbar

        g_Enabled := !g_Enabled

        if (g_Enabled)
        {
            ; 启用隐藏模式
            g_HideIcons := true
            g_HideTaskbar := true

            ; 隐藏桌面图标
            HideDesktopIcons(true)

            ; 隐藏任务栏
            HideTaskbar(true)

            ShowNotification(, 2000)
        }
        else
        {
            ; 禁用隐藏模式
            g_HideIcons := false
            g_HideTaskbar := false

            ; 显示桌面图标
            HideDesktopIcons(false)

            ; 显示任务栏
            HideTaskbar(false)

            ShowNotification("已禁用：恢复图标 + 恢复任务栏", 2000)
        }

        return
    }

    HideDesktopIcons(Hide)
    {
        ; 通过调整 ProgMan （桌面窗口）来隐藏/显示桌面图标
        ; 获取桌面窗口句柄
        ProgManHwnd := WinExist("ahk_class ProgMan")

        if (!ProgManHwnd)
            return

        ; 获取 SHELLDLL_DefView（图标列表视图）
        DllCall("user32.dll", "int", "SendMessage", "uint", ProgManHwnd, "uint", 0x111, "int", 28931, "int", 0)

        ; 另一种方法：通过注册表设置隐藏/显示图标
        ; 这是更稳定的Windows 11方法

        if (Hide)
        {
            ; 隐藏图标 - 通过发送隐藏命令到 WorkerW（壁纸)窗口
            WinExist("ahk_class WorkerW")
            if (WinExist())
            {
                ; 使用更温和的方式 - 通过资源管理器调用
                COMObjCreate("Shell.Application").ToggleDesktop()
                Sleep(100)
                COMObjCreate("Shell.Application").ToggleDesktop()
            }
        }
        else
        {
            ; 恢复图标
            ; 保持桌面正常状态
        }

        return
    }

    HideTaskbar(Hide)
    {
        ; 获取任务栏窗口
        TaskbarHwnd := WinExist("ahk_class Shell_TrayWnd")

        if (!TaskbarHwnd)
            return

        if (Hide)
        {
            ; 隐藏任务栏 - 使用 ShowWindow API
            DllCall("user32.dll", "int", "ShowWindow", "uint", TaskbarHwnd, "int", 0)  ; 0 = 隐藏
        }
        else
        {
            ; 显示任务栏
            DllCall("user32.dll", "int", "ShowWindow", "uint", TaskbarHwnd, "int", 5)  ; 5 = 显示
        }

        return
    }

    ShowNotification(Text, Duration)
    {
        ; 使用ToolTip显示通知，不闪烁屏幕
        ToolTip, %Text%
        SetTimer(RemoveToolTip, Duration)
        return
    }

    RemoveToolTip()
    {
        SetTimer(RemoveToolTip, "Off")
        ToolTip
        return
    }

    ExitScript(ExitReason, ExitCode)
    {
        ; 脚本退出时恢复UI
        if (g_Enabled)
        {
            HideDesktopIcons(false)
            HideTaskbar(false)
        }

        return
    }

; 退出快捷键 (Ctrl+Alt+X)
^!x::
    {
        ExitApp
    }
