-----

# 🦅 Vult-RAT: Advanced Remote Administration & Security Auditing

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Maintained%3F-Yes-green?style=for-the-badge" alt="Maintained">
</p>


**Vult-RAT** is a high-performance, modular Remote Access Trojan (RAT) architecture. Engineered for stealth and deep system integration, it features a custom **Batch Builder** for tailored payload generation and a robust Discord-based C2 (Command & Control) interface.

-----

## 🔥 Key Features

  * 🚀 **Universal Bypass:** Specifically engineered to evade **Windows Defender** and **360 Protection** heuristics.
  * 🛠️ **Custom Builder:** Use `builder.bat` to inject icons, toggle console visibility, and compress payloads.
  * 🛰️ **Discord C2:** Full real-time control over target machines via a private Discord bot.
  * 🕵️ **Total Surveillance:** Remote Keylogging, Webcam capture, and Microphone recording modules.
  * 🛡️ **Persistence Engine:** Advanced modules for Startup integration, Rootkit-style hiding, and UAC bypass.
  * 💾 **Exfiltration:** Automated dumping of Chromium passwords and Discord session tokens.

-----

## 📸 Preview

### 📺 Video Showcase

[](https://www.youtube.com/watch?v=QdYh2lCtzf0)

> *Note: This is the guide if you need to watch this.*

### 🛠️ The Builder Interface

The tool includes a standalone `.bat` builder for masquerading.

  * **Name:** Set the internal process name to blend with system tasks.
  * **Icon:** Inject any `.ico` file to make the executable look legitimate.
  * **Stealth:** Toggle "No Console" mode for silent background execution.

-----

## 📜 Complete Command Reference

> **Legend:** `[!]` = Requires Admin Privileges | `< >` = Required Argument

### 🛠️ Core Commands

| Command | Action |
| :--- | :--- |
| `!message <text>` | Show a custom popup message box |
| `!shell <cmd>` | Execute a raw shell command |
| `!voice <text>` | Text-to-Speech (System Speakers) |
| `!admincheck` | Verify current privilege status |
| `!sysinfo` | Full System & Hardware profile |
| `!publicip` | Show target's public IP address |
| `!geolocate` | High-precision IP intelligence |

### 📂 File System Management

| Command | Action |
| :--- | :--- |
| `!cd <path>` | Change working directory |
| `!dir` | List all files in current path |
| `!currentdir` | Show current working path |
| `!download <file>` | Pull file from target to C2 |
| `!upload` | Push file to target (Attach file to msg) |
| `!uploadlink <url>`| Download file from direct URL |
| `!delete <file>` | Permanently delete a file |
| `!write <text>` | Simulate keyboard typing |

### 👁️ Surveillance & OSINT

| Command | Action |
| :--- | :--- |
| `!screenshot` | Capture high-res desktop view |
| `!webcampic` | Capture remote webcam snapshot |
| `!getcams` | List all available camera devices |
| `!mic <seconds>` | Record microphone audio |
| `!keylog <cmd>` | Start / Stop / Dump keystroke logs |
| `!clipboard` | Get current clipboard content |

### ⚙️ System Control & Persistence

| Command | Action |
| :--- | :--- |
| `!shutdown` / `!restart`| Remote Power Control |
| `!bluescreen` `[!]` | Trigger manual BSOD |
| `!block` / `!unblock` `[!]`| Lock/Unlock Mouse and Keyboard |
| `!disabletaskmgr` | Disable Task Manager via Registry |
| `!prockill <name>` | Terminate a specific process |
| `!startup <add/remove>`| Add/Remove from system boot |
| `!rootkit` `[!]` | Hide process from Task Manager |
| `!critproc` `[!]` | Make process critical (BSOD on kill) |
| `!uacbypass` | Attempt privilege escalation |

### 🔐 Security & Misc

| Command | Action |
| :--- | :--- |
| `!password` | Dump stored Chrome credentials |
| `!grabtokens` | Extract Discord session tokens |
| `!disabledefender` `[!]`| Kill Windows Defender |
| `!disablefirewall` `[!]`| Turn off Windows Firewall |
| `!wallpaper` | Change desktop background |
| `!website <url>` | Force open a website |
| `!exit` | Self-destruct / Kill agent |

-----

## 🛠️ Installation & Setup

### 1\. Clone & Prep

```bash
git clone https://github.com/jumpedoverjumpman/Vult-RAT.git
cd Vult-RAT
```

### 2\. Install Dependencies

```bash
pip install discord.py opencv-python pyaudio wave keyboard psutil pyautogui requests pywin32
```

### 3\. Build the Payload

1.  Place your target `.ico` in the root folder.
2.  Run `builder.bat`.
3.  Enter your Discord Bot Token and Channel ID when prompted.
4.  Distribute the generated `.exe` for authorized security auditing.

-----

## ⚠️ Legal Disclaimer

**FOR EDUCATIONAL AND SECURITY RESEARCH PURPOSES ONLY.**
This project is designed to demonstrate remote access vulnerabilities and to test antivirus detection logic in controlled environments.

  * **DO NOT** use this tool for unauthorized access.
  * Always test inside an **Isolated Virtual Machine (VM)** or sandbox.
  * The developer (**Vultures**) assumes zero liability for misuse of this information.

-----

**Developed with ❤️ by [Vultures](https://www.google.com/search?q=https://github.com/jumpedoverjumpman)**
