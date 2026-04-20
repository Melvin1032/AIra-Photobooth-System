# AIra Pro Photobooth - Deployment Guide

## 📦 Part 1: Creating the Executable (.exe)

### Quick Build

```bash
python build_exe.py
```

This will create: `dist/AIraPhotobooth.exe` (~100-150 MB)

### Manual Build (Alternative)

```bash
pyinstaller --name AIraPhotobooth --windowed --onefile --add-data "config.json;." --add-data "frames;frames" main.py
```

### Testing the .exe

1. Navigate to `dist/` folder
2. Double-click `AIraPhotobooth.exe`
3. Test all features:
   - Camera preview
   - Photo capture
   - QR code generation
   - Download page

### Distribution

**Option A: Direct .exe**
- Share `AIraPhotobooth.exe` directly
- Users double-click to run
- No installation needed

**Option B: Create Installer (Recommended)**
Use tools like:
- **Inno Setup** (Free): https://jrsoftware.org/isdl.php
- **NSIS** (Free): https://nsis.sourceforge.io/

---

## 🌐 Part 2: Cloudflare Tunnel Setup

### What is Cloudflare Tunnel?

Cloudflare Tunnel creates a secure, free connection from the internet to your local photobooth server. Students can scan QR codes and download photos from **ANY network** - not just the same WiFi.

### How It Works

```
Student Phone (Any Network)
        ↓
    Internet
        ↓
Cloudflare Tunnel (Free)
        ↓
Your Laptop (Local Server)
        ↓
   Photo Files
```

### Automatic Setup (Built-in)

The app now includes **automatic Cloudflare Tunnel setup**:

1. **Launch the app**
2. **Go to Settings panel** (right side)
3. **Click "🌐 Local Network" button**
4. **Wait 10-30 seconds** for tunnel to start
5. **Button changes to "🌐 Internet Mode"**
6. **Status indicator turns BLUE**

That's it! QR codes now work from any network!

### Manual Installation (Optional)

If automatic installation fails:

**Windows:**
```powershell
# Download cloudflared
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

# Test it
.\cloudflared --version
```

**macOS:**
```bash
brew install cloudflared
```

**Linux:**
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

---

## 🎓 Part 3: School Event Deployment

### Before the Event

**1. Test Everything**
```
☐ Test camera works
☐ Test photo capture
☐ Test frame overlays
☐ Test QR code scanning (from phone)
☐ Test download page loads
☐ Test internet mode (if using)
```

**2. Prepare the Setup**
- Install app on event laptop
- Connect webcam
- Test internet connection (if using Cloudflare)
- Print QR code test page

**3. Backup Plan**
- Keep local mode as fallback
- Have USB export ready
- Test offline functionality

### At the Event

**Setup Checklist:**
```
1. ☐ Connect laptop to power
2. ☐ Connect webcam
3. ☐ Launch AIraPhotobooth.exe
4. ☐ Connect to WiFi (if needed)
5. ☐ Enable Internet Mode (optional)
6. ☐ Test QR scan with your phone
7. ☐ Start photobooth!
```

**Network Mode Decision:**

| Mode | When to Use | Pros | Cons |
|------|-------------|------|------|
| **Local** | Small events, same WiFi | Fast, no internet needed | Same network only |
| **Internet** | Large events, multiple networks | Works anywhere | Needs internet |

### After the Event

**Data Collection:**
1. Export session log (CSV)
2. Export photos to USB
3. Backup `events/` folder
4. Clear old sessions (optional)

---

## 🔧 Troubleshooting

### .exe Won't Build

**Issue:** PyInstaller errors
```bash
# Fix:
pip install --upgrade pyinstaller
pip install -r requirements.txt
python build_exe.py
```

### .exe Triggers Antivirus

**Issue:** Windows SmartScreen warning
**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. (Optional) Code-sign the .exe for production

### Cloudflare Tunnel Won't Start

**Issue:** Tunnel fails to initialize
**Solutions:**
```
1. Check internet connection
2. Try again in 30 seconds
3. Check firewall isn't blocking
4. Manual install cloudflared (see above)
```

### QR Code Not Scanning

**Issue:** Phone can't scan QR
**Solutions:**
1. Increase screen brightness
2. Hold phone 6-12 inches away
3. Check URL in QR code is correct
4. Test with QR scanner app

### Download Page Not Loading

**Issue:** QR scans but page won't load
**Solutions:**
1. Check internet connection
2. Verify tunnel is running (blue status)
3. Try accessing URL manually
4. Check Windows Firewall allows port 8080

---

## 📊 Cloudflare Tunnel - Free Tier Limits

**Good news:** Cloudflare Tunnel is **100% FREE** with NO LIMITS!

✅ Unlimited bandwidth  
✅ Unlimited connections  
✅ No time limits  
✅ No branding  
✅ Custom domains (optional)  

Perfect for school events!

---

## 🚀 Pro Tips for School Events

### Performance
- Use SSD for faster photo saving
- Close other apps during event
- Keep laptop plugged in
- Use wired internet if possible

### QR Code Best Practices
- Test scan before event starts
- Keep screen brightness at 80%+
- Position monitor at eye level
- Have backup USB export ready

### Internet Mode
- Start tunnel 5 minutes before event
- Test with student phones
- Have local mode as fallback
- Monitor tunnel status (blue dot)

### Data Management
- Create new event for each school
- Export data after each event
- Backup photos to cloud/USB
- Clear old sessions monthly

---

## 📞 Support

**Common Questions:**

**Q: Do students need internet to scan QR?**  
A: Only if using Internet Mode. Local mode works on same WiFi without internet.

**Q: How many students can download simultaneously?**  
A: Unlimited! Cloudflare handles traffic automatically.

**Q: Do photos stay on my computer?**  
A: Yes! All photos saved locally. Cloudflare only creates temporary access.

**Q: Can I use custom domain?**  
A: Yes! With Cloudflare account (free), you can use custom domains.

**Q: What if internet goes down?**  
A: Switch to Local Mode. QR codes will work on same WiFi.

---

## 🎉 Success Checklist

Before deploying to schools:

```
☐ .exe builds successfully
☐ App runs without Python installed
☐ Camera works on target laptop
☐ QR codes scan from phones
☐ Download page loads correctly
☐ Internet mode works (if needed)
☐ USB export functions
☐ CSV export works
☐ All features tested end-to-end
☐ Backup plan ready
```

**You're ready! Good luck with your school events! 🎓📸**
