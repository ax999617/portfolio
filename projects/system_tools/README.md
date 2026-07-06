# System Tools

Source provenance:

- Runtime path supplied by user: `C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe`
- Located user scripts: `D:\shiwanwuax\haiku4.5\AutoHotkey`
- Source CSV: none identified in this asset set

## Problem definition

This utility project preserves a small Windows desktop automation tool used to toggle desktop UI visibility. It is intentionally presented as a supporting utility, not a main portfolio project.

## Method

The tool uses AutoHotkey scripts to monitor a trigger gesture and hide or show desktop icons and the taskbar. The source scripts include a Windows 11 enhanced variant and setup/troubleshooting batch files.

## Implementation

- `scripts/DesktopUIToggle.ahk` preserves the original script.
- `scripts/DesktopUIToggle_Enhanced.ahk` preserves the enhanced Windows 11 version.
- `scripts/*.bat` preserve setup, run, removal, and troubleshooting helpers.

Compatibility note: the supplied runtime path points to AutoHotkey v2, while the discovered scripts use AutoHotkey v1-style syntax and source comments. This repository records the mismatch but does not modify the scripts.

## How to run

Install a compatible AutoHotkey runtime for the script version, then run:

```bat
scripts\RunScript.bat
```

Use the setup batch file only after reviewing the script behavior.

## Results

The utility is organized as a low-priority automation example showing Windows scripting, startup integration, and desktop UI control. No system settings were changed during portfolio consolidation.
