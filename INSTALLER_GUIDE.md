# 📦 AIra Pro Photobooth - Installer Creation Guide

## 🎯 Overview

This guide will help you create a professional Windows installer for your photobooth application.

---

## 📋 Prerequisites

### Step 1: Download Inno Setup (FREE)

1. Visit: **https://jrsoftware.org/isdl.php**
2. Download **"Inno Setup 6.x.x"** (latest version)
3. Run the installer and complete installation
4. Default location: `C:\Program Files (x86)\Inno Setup 6\`

---

## 🛠️ Build the Installer

### Step 1: Build the .exe (if not already done)

```bash
python build_exe.py
```

This creates `dist/AIraPhotobooth.exe` (148.3 MB)

### Step 2: Build the Installer

```bash
python build_installer.py
```

This will:
- ✅ Check for Inno Setup
- ✅ Bundle all required files
- ✅ Create professional installer
- ✅ Output to `installer_output/` folder

### Expected Output:

```
============================================================
  ✅ INSTALLER READY!
============================================================
📦 Installer: installer_output/AIraPhotobooth_Setup_v2.1.exe
📊 Size: ~155 MB
```

---

## 📦 What's Included in the Installer

The installer automatically packages:

| File/Folder | Purpose |
|------------|---------|
| `AIraPhotobooth.exe` | Main application |
| `cloudflared.exe` | Cloudflare Tunnel for internet mode |
| `config.json` | Application configuration |
| `frames/` | Photo frame templates |
| `assets/` | Logo, icons, and other assets |
| `events/` | Photo storage (auto-created) |
| `logs/` | Application logs (auto-created) |

---

## 💻 Installation Process (End User)

When someone runs the installer, they'll see:

1. **Welcome Screen** - Professional wizard interface
2. **License Agreement** - (optional, can add later)
3. **Choose Install Location** - Default: `C:\Program Files\AIra Pro Photobooth\`
4. **Choose Start Menu Folder** - Default: `AIra Pro Photobooth`
5. **Select Additional Tasks**:
   - ☑️ Create desktop shortcut
   - ☑️ Create Quick Launch icon
6. **Installing** - Progress bar
7. **Completing** - Option to launch immediately

**After installation:**
- ✅ Desktop shortcut created
- ✅ Start Menu entry created
- ✅ Uninstaller added to Control Panel
- ✅ App ready to use!

---

## 🔄 Update/Uninstall

### To Update:
1. Run new installer over existing installation
2. Installer will automatically replace old files

### To Uninstall:
- **Method 1**: Control Panel → Programs → Uninstall AIra Pro Photobooth
- **Method 2**: Start Menu → AIra Pro Photobooth → Uninstall
- **Method 3**: Run `unins000.exe` in installation folder

---

## 🎨 Customization (Optional)

### Add Your Logo to Installer

Edit `installer_setup.iss` and update these lines:

```ini
SetupIconFile=assets\LOGO.png          ; Icon on installer window
WizardImageFile=installer_banner.bmp   ; Large banner (164x314 px)
WizardSmallImageFile=installer_logo.bmp ; Small logo (55x55 px)
```

### Add License Agreement

1. Create `LICENSE.txt` with your terms
2. Edit `installer_setup.iss`:
   ```ini
   LicenseFile=LICENSE.txt
   ```

### Change App Information

Edit the `#define` section at the top of `installer_setup.iss`:

```ini
#define MyAppName "AIra Pro Photobooth"
#define MyAppVersion "2.1"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://yourwebsite.com"
```

---

## 📊 Distribution

### USB Drive Distribution
1. Copy `installer_output/AIraPhotobooth_Setup_v2.1.exe` to USB
2. Plug into target computer
3. Run installer

### Cloud Storage Distribution
1. Upload installer to Google Drive, Dropbox, etc.
2. Share download link with users
3. Users download and run

### Network Distribution
1. Place installer on shared network drive
2. Users access from network location
3. Run installer locally on each machine

---

## ⚠️ Important Notes

1. **Antivirus**: The .exe may trigger SmartScreen (normal for unsigned apps)
   - Click "More info" → "Run anyway"
   - For professional use, consider code signing certificate ($200-400/year)

2. **Administrator Rights**: The installer uses `lowest` privileges
   - Installs to user's AppData if no admin rights
   - Installs to Program Files if admin rights available

3. **Dependencies**: Everything is bundled in the installer
   - No Python installation required
   - No additional downloads needed
   - Fully standalone

---

## 🚀 Quick Start Summary

```bash
# 1. Install Inno Setup
# Download from: https://jrsoftware.org/isdl.php

# 2. Build the executable
python build_exe.py

# 3. Build the installer
python build_installer.py

# 4. Distribute the installer
# File: installer_output/AIraPhotobooth_Setup_v2.1.exe
```

---

## 🆘 Troubleshooting

### "Inno Setup not found"
- Make sure Inno Setup is installed
- Default path: `C:\Program Files (x86)\Inno Setup 6\`
- Re-download from https://jrsoftware.org/isdl.php

### "dist/AIraPhotobooth.exe not found"
- Run `python build_exe.py` first
- Check that build completed successfully

### Installer is too large
- Normal size: ~155 MB (includes Python, PyQt6, OpenCV)
- Can't be reduced without removing features

---

## 📞 Support

For issues or questions:
- Check logs in: `C:\Users\[Username]\AppData\Local\AIra Pro Photobooth\logs\`
- Review application logs: `[InstallDir]\logs\app.log`

---

**Enjoy your professional photobooth application! 📸✨**
