# QR Code Scanning Troubleshooting Guide

## Issues Fixed in This Update

### 1. QR Code Generation Improvements
- ✅ **Increased error correction** from ERROR_CORRECT_M (15%) to ERROR_CORRECT_H (30%) for better scanability
- ✅ **Increased QR code size** from 280px to 300px for better detection
- ✅ **Added white border padding** (40px) around QR code for improved scanner detection
- ✅ **Maintained NEAREST resampling** to preserve sharp module edges (no blurring)
- ✅ **Increased display size** from 240x240 to 260x260 pixels

### 2. Better Diagnostic Logging
- ✅ Server startup now shows clear success messages with checkmarks
- ✅ QR generation logs URL length and QR version
- ✅ Shows error correction level being used
- ✅ Displays final QR code size

## Quick Test Steps

### Step 1: Run the QR Code Test
```bash
python test_qr_code.py
```

This will:
- Start the QR server
- Generate a QR code for an existing photo
- Save it as `test_qr_code.png`
- Show you the exact URL encoded in the QR code

### Step 2: Test the QR Code
1. Open `test_qr_code.png` on your computer screen
2. Try scanning it with your phone
3. If it scans, you should see a download page with your photo

### Step 3: If QR Code Still Doesn't Scan

#### Check 1: URL Accessibility
The QR code contains a URL like: `http://192.168.1.XX:8080/PhotoName.jpg`

**Test from your phone's browser:**
1. Connect your phone to the same WiFi network as your computer
2. Open browser and manually type the URL shown in the test output
3. If the page loads → QR generation is the issue
4. If the page doesn't load → Network/firewall is the issue

#### Check 2: Windows Firewall
The QR server needs to accept incoming connections:

**Add Windows Firewall Exception:**
```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "AIra Photobooth QR Server" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

**Or manually:**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → TCP → Specific local ports: `8080`
5. Select "Allow the connection"
6. Check all profiles (Domain, Private, Public)
7. Name it "AIra Photobooth QR Server"

#### Check 3: Network Configuration
- Your computer and phone MUST be on the same WiFi network
- Check your computer's IP address:
  ```powershell
  ipconfig
  ```
  Look for "IPv4 Address" under your WiFi adapter (e.g., 192.168.1.XX)

#### Check 4: Port Availability
If port 8080 is blocked, the server will try other ports. Check the console output:
```
[QR SERVER] ✓ Started successfully at http://192.168.1.XX:8080
```

If it shows a different port, that's the one you need to allow in firewall.

#### Check 5: QR Code Display Quality
- Make sure the QR code is displayed on a bright, high-contrast screen
- Avoid glare or reflections on the screen
- Hold phone 6-12 inches away from screen
- Try adjusting phone camera focus

## Common Issues & Solutions

### Issue: "Nothing shows on phone when scanning"
**Solutions:**
1. The QR code might not be encoding a valid URL - check test output
2. Your phone might not be connected to the same network
3. Firewall is blocking the connection
4. The URL in the QR code uses the wrong IP address

### Issue: "QR code shows URL but page won't load"
**Solutions:**
1. Check Windows Firewall (see Check 2 above)
2. Verify phone and computer are on same network
3. Try accessing the URL manually from phone browser
4. Check if another program is using port 8080

### Issue: "QR code is hard to scan / takes multiple tries"
**Solutions:**
1. Increase screen brightness
2. Clean phone camera lens
3. Hold phone steady at proper distance
4. The QR code should now be larger and more scannable with the recent fixes

### Issue: "IP address in QR code is wrong"
The QR server detects your local IP automatically. If it's wrong:
1. Check your actual IP: `ipconfig`
2. The server uses the IP that can reach 8.8.8.8 (Google DNS)
3. If you have multiple network adapters, it might pick the wrong one
4. You may need to manually specify the IP in the code

## What Changed in the Code

### core/qr_server.py
- Changed `ERROR_CORRECT_M` → `ERROR_CORRECT_H` (better error correction)
- Changed default size: `280` → `300` pixels
- Added white border padding: `ImageOps.expand(qr_img, border=40, fill='white')`
- Enhanced logging with checkmarks and detailed information

### ui/viewer_window.py
- Increased QR label size: `240x240` → `260x260` pixels
- Increased QR display size: `210x210` → `230x230` pixels
- Already using `FastTransformation` (correct - no blurring)

## Testing Checklist

After making these changes:

- [ ] Run `python test_qr_code.py` successfully
- [ ] QR code image is generated and saved
- [ ] QR code scans with phone camera
- [ ] Download page loads on phone browser
- [ ] Photo displays on the download page
- [ ] Download button works
- [ ] In the actual app, QR code appears after photo capture
- [ ] QR code in the app is scannable

## Need More Help?

If the QR code still doesn't work after following all steps:

1. **Share the console output** when you run the test
2. **Share what happens** when you scan (any error messages?)
3. **Share your IP address** and network setup
4. **Try a different QR scanner app** (some phones' built-in scanners are picky)

The most common issue is **Windows Firewall blocking port 8080** - make sure to add the exception!
