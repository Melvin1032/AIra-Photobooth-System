# SnapFrame Pro - UI Test Build

Complete, testable UI for the SnapFrame Pro photobooth application.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

The application will launch with:
- ✅ Full operator dashboard
- ✅ Mock data pre-loaded
- ✅ All buttons clickable
- ✅ Dark theme (default)

---

## 🎨 Features Available for Testing

### Operator Dashboard
- **5-Panel Layout**: Top bar, left panel, center, right panel, bottom bar
- **Frame Selector**: Grid of 5 mock frames with selection
- **Live Preview Area**: Placeholder preview with countdown overlay
- **Session Log Table**: 10+ sample sessions with edit/delete buttons
- **Theme Toggle**: Dark ↔ Light mode switch

### Interactive Elements

| Button | Action |
|--------|--------|
| `📸 CAPTURE` | Starts 3-second countdown → shows mock photo → returns to preview |
| `🖨️ Print` | Opens print dialog (UI only) |
| `👁️ Viewer` | Toggles secondary viewer window |
| `🌙 Dark/☀️ Light` | Switches theme |
| `➕ Create Event` | Creates mock event |
| `📂 Load Event` | Loads from mock event list |
| `✏️ Edit Event` | Edits current event name |
| `🗑️ Delete Event` | Deletes current event |
| `🆕 New Session` | Resets session form |
| `💾 USB Export` | Shows mock message |
| `📊 CSV Export` | Shows mock message |
| `+ Add Frame` | Shows mock upload dialog |
| `✏️ (session)` | Edits session (table action) |
| `🗑️ (session)` | Deletes session (table action) |

### Viewer Window (Secondary Display)
- Full-screen capable
- Idle/attract screen
- Live preview placeholder
- Countdown display
- Final photo display

---

## 📁 File Structure

```
Photobooth/
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── config.json                # Theme/settings
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── ui/
│   ├── __init__.py
│   ├── operator_window.py     # Main dashboard (661 lines)
│   ├── viewer_window.py       # Secondary display (188 lines)
│   ├── frame_selector.py      # Frame grid (328 lines)
│   ├── session_log_table.py   # Session history (229 lines)
│   ├── countdown_overlay.py   # Countdown animation (140 lines)
│   └── print_dialog.py        # Print dialog (218 lines)
├── assets/
│   └── icons/                 # (Optional) Icon files
└── frames/                    # Frame storage
```

---

## 🧪 Testing Guide

### Test 1: Basic UI Launch
```bash
python main.py
```
**Expected**: Window opens within 5 seconds, all panels visible

### Test 2: Theme Toggle
1. Click `🌙 Dark` button in top bar
2. UI switches to light theme
3. Click `☀️ Light` to return to dark

### Test 3: Frame Selection
1. Click any frame in left panel
2. Frame highlights in gold
3. Frame info updates in center panel

### Test 4: Capture Flow
1. Select a frame (required)
2. Click `📸 CAPTURE`
3. Countdown overlay appears (3, 2, 1)
4. Mock photo displayed for 3 seconds
5. Returns to live preview

### Test 5: Viewer Window
1. Click `👁️ Viewer` button
2. Secondary window opens
3. Shows idle screen
4. During capture, shows countdown and photo
5. Click `👁️ Hide Viewer` to close

### Test 6: Session Management
1. Look at bottom panel (Session Log)
2. 10 sample sessions displayed
3. Click `✏️` to edit (mock dialog)
4. Click `🗑️` to delete (with confirmation)

### Test 7: Event Management
1. Click `➕ Create Event`
2. Enter event name
3. Event created, Edit/Delete buttons appear
4. Try editing and deleting

---

## 🎨 Theme Colors

### Dark Mode (Default)
- Background: `#0a0a0a` (main), `#1a1a1a` (panels), `#2d2d2d` (widgets)
- Gold Primary: `#FFD700`
- Gold Secondary: `#D4AF37`
- Text: `#ffffff`

### Light Mode
- Background: `#ffffff`, `#f5f5f5`, `#e0e0e0`
- Gold: `#D4AF37`
- Text: `#000000`

---

## 🔌 Connecting Backend

To connect real functionality, replace these mock methods:

### Camera Integration
**File**: `ui/operator_window.py`
**Method**: `_simulate_capture()`
```python
# Replace with actual camera capture
def _on_capture_clicked(self):
    # ... countdown code ...
    # Instead of _simulate_capture(), call actual capture
    self.camera.capture_photo()
```

### Database Integration
**File**: `ui/operator_window.py`
**Methods**: `_on_create_event()`, `_on_load_event()`
```python
# Replace mock event creation with database call
event_id = self.db.create_event(name, date, venue)
```

### Print Integration
**File**: `ui/print_dialog.py`
**Method**: `_on_print()`
```python
# Replace with actual print call
printer.print_photo(self.photo_path, copies=self.copies_spin.value())
```

---

## 📊 Performance

Optimized for low-end PCs:
- ✅ No heavy dependencies (only PyQt6 + Pillow)
- ✅ Efficient widget rendering
- ✅ Minimal startup time (< 5 seconds)
- ✅ Smooth UI interactions

---

## 🐛 Troubleshooting

### Issue: Window doesn't open
**Solution**: Check PyQt6 installation
```bash
pip install PyQt6 --upgrade
```

### Issue: UI looks wrong
**Solution**: Delete config.json and restart

### Issue: Buttons not responding
**Solution**: Check console for Python errors

---

## 📝 Mock Data Included

### Events
- Wedding - Santos & Reyes (2026-04-15)
- Birthday Party - Alex (2026-04-20)
- Corporate Event - XYZ Corp (2026-04-25)

### Frames
- Classic Gold Frame (2 shots, ₱500)
- Floral Border (1 shot, ₱500)
- Modern Minimalist (4 shots, ₱750)
- Vintage Style (3 shots, ₱600)
- Elegant Black (2 shots, ₱550)

### Sessions
10 sample sessions with various clients, frames, and payment statuses.

---

## 🎯 Success Criteria Checklist

- [x] App launches in < 5 seconds
- [x] All panels visible and properly laid out
- [x] Theme toggle works (dark ↔ light)
- [x] Session table shows 10+ sample rows
- [x] Frame selector shows 5 mock frames
- [x] All buttons clickable with visual feedback
- [x] No errors in console
- [x] Looks professional and modern
- [x] Capture flow works (mock)
- [x] Viewer window functional

---

## 📄 License

Internal use for SnapFrame Pro development.

---

**Version**: 2.1.0 (UI Test Build)  
**Last Updated**: April 2026
