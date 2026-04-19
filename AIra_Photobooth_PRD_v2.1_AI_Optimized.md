# AIra Photobooth System - PRD v2.1 (AI-Optimized)

> **Document Type**: Product Requirements Document  
> **Version**: 2.1 (AI-Optimized for Agent Understanding)  
> **Date**: April 2026  
> **System Name**: AIra Photobooth System / SnapFrame Pro  
> **Platform**: Windows 10/11 Desktop Application  
> **Technology**: Python 3.11+ with PyQt6

---

## 📖 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Project Goals & Priorities](#3-project-goals--priorities)
4. [User Personas](#4-user-personas)
5. [System Architecture](#5-system-architecture)
6. [Core Features](#6-core-features)
7. [UI/UX Specifications](#7-uiux-specifications)
8. [Performance Requirements](#8-performance-requirements)
9. [Database Schema](#9-database-schema)
10. [File Structure](#10-file-structure)
11. [Development Phases](#11-development-phases)
12. [Risk Management](#12-risk-management)
13. [Implementation Status](#13-implementation-status)
14. [Future Roadmap](#14-future-roadmap)

---

## 1. Executive Summary

### What is AIra Photobooth?

AIra Photobooth is a **professional desktop application** for freelance photographers that automates the entire photobooth workflow:

- **Tethered camera capture** (DSLR or webcam)
- **Real-time live preview** on dual monitors
- **Automatic photo compositing** with custom frame templates
- **Session management** with payment tracking
- **Instant printing** and USB export
- **Offline-first** (no internet required)

### Key Value Proposition

Replace a **manual, multi-step process** (camera → SD card → Photoshop → print) with a **single-click automated workflow** that handles everything from capture to delivery in under 10 seconds.

---

## 2. Problem Statement

### Current Manual Workflow (PAIN POINTS)

| Step | Manual Process | Time Required | Problems |
|------|---------------|---------------|----------|
| 1 | Remove SD card from camera | 30s | Disrupts workflow |
| 2 | Transfer photos to computer | 1-2 min | Manual file management |
| 3 | Open Adobe Photoshop | 30s | Requires expensive software |
| 4 | Place photos into frame template | 2-5 min | Error-prone, inconsistent |
| 5 | Save and print | 1-2 min | Manual printer selection |
| 6 | Deliver to client | 30s | No digital copy system |

**Total time per session**: 5-10 minutes  
**Problems**:
- ❌ No live client preview during capture
- ❌ No session logging (customers, frames, revenue tracked manually)
- ❌ Unscalable for high-traffic events (50-200 guests)
- ❌ Requires Photoshop expertise
- ❌ No standardized digital delivery

### Solution

Automate the entire workflow into a **single application** that:
- ✅ Captures directly from camera (tethered)
- ✅ Shows live preview to clients
- ✅ Auto-composites photos into frames (< 3 seconds)
- ✅ Logs all session data automatically
- ✅ One-click printing
- ✅ USB digital delivery

---

## 3. Project Goals & Priorities

### CRITICAL (Must Have - MVP)

| ID | Goal | Description | Success Metric |
|----|------|-------------|----------------|
| **G-01** | Tethered Camera Capture | Camera connected directly to software, no SD card | Photos download automatically |
| **G-02** | Auto-Compositing | Combine photos with frame template | < 3 seconds processing time |
| **G-03** | Live Preview | Real-time camera feed on second monitor | 15+ fps, low latency |
| **G-04** | Custom Frame Support | Upload PNG+JSON frame templates per event | Any size/slot configuration |
| **G-05** | Session Logging | Track client, frame, payment, timestamp | Complete database records |

### HIGH (Should Have)

| ID | Goal | Description | Success Metric |
|----|------|-------------|----------------|
| **G-06** | One-Click Print | Print to Epson printer with one click | < 5 seconds to queue |
| **G-07** | USB Export | Save photo to client's USB drive | Auto-detect + copy |
| **G-08** | Dual Capture Modes | Auto-countdown AND manual trigger | Both modes work flawlessly |
| **G-09** | Portable | Single folder, no complex install | Runs from USB drive |

### MEDIUM (Nice to Have)

| ID | Goal | Description | Success Metric |
|----|------|-------------|----------------|
| **G-10** | Camera Settings UI | Adjust ISO, aperture from software | All settings accessible |
| **G-11** | Event Reports | Daily summary, CSV export | One-click export |
| **G-12** | Performance Optimization | Smooth on low-end hardware | 60fps UI, < 10s startup |

---

## 4. User Personas

### Persona 1: Operator (Photographer) - PRIMARY USER

**Profile**: Freelance event photographer, non-technical, values speed and reliability

**Goals**:
- Process 50-200 clients per event efficiently
- Zero technical issues during events
- Professional results with minimal effort
- Track revenue and sessions automatically

**Pain Points**:
- Manual Photoshop work is time-consuming
- Can't focus on clients when managing files
- No reliable backup of session data

**Key Features Needed**:
- One-click capture workflow
- Automatic compositing
- Session log with payment tracking
- Reliable camera connection
- Quick frame setup (< 5 min per event)

### Persona 2: Client / Guest - VIEWER

**Profile**: Event attendee, wants fun experience and quality photos

**Goals**:
- See themselves in real-time before photo
- Get printed photo immediately
- Optional digital copy for social media

**Pain Points**:
- Waiting 5-10 minutes for edited photos
- No preview during capture
- Awkward posing without mirror/preview

**Key Features Needed**:
- Live preview on second screen
- Fast delivery (< 30 seconds)
- Clear countdown timer
- USB digital copy option

### Persona 3: Event Organizer - INDIRECT STAKEHOLDER

**Profile**: Wedding planner, corporate event coordinator

**Goals**:
- Reliable photobooth service
- Branded photo experience
- Session report for billing

**Pain Points**:
- Unreliable vendors
- No data on guest engagement
- Manual headcount needed

**Key Features Needed**:
- Event-specific branding (custom frames)
- Session count reports
- Professional presentation

---

## 5. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AIra Photobooth System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐          ┌──────────────────┐         │
│  │   Operator        │  Signals │   Viewer          │         │
│  │   Dashboard       │◄────────►│   Dashboard       │         │
│  │   (QMainWindow)   │  /Slots  │   (QWidget)       │         │
│  └────────┬─────────┘          └────────┬──────────┘         │
│           │                             │                     │
│           └──────────┬──────────────────┘                     │
│                      │                                        │
│           ┌──────────▼──────────┐                            │
│           │   Core Services      │                            │
│           ├─────────────────────┤                            │
│           │ • Camera Manager    │                            │
│           │ • Photo Compositor  │                            │
│           │ • Session Manager   │                            │
│           │ • Print Manager     │                            │
│           │ • USB Exporter      │                            │
│           │ • Recovery Manager  │                            │
│           └──────────┬──────────┘                            │
│                      │                                        │
│           ┌──────────▼──────────┐                            │
│           │   Data Layer         │                            │
│           ├─────────────────────┤                            │
│           │ • SQLite Database   │                            │
│           │ • File System       │                            │
│           │ • Config (JSON)     │                            │
│           └─────────────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Core application |
| **UI Framework** | PyQt6 | 6.x | Dual-window desktop UI |
| **Camera (DSLR)** | digiCamControl API | Latest | Canon/Nikon tethering (Windows) |
| **Camera (Webcam)** | OpenCV (cv2) | 4.x | Webcam/IP camera fallback |
| **Image Processing** | Pillow (PIL) | 10.x | PNG compositing, JPEG output |
| **Database** | SQLite3 | stdlib | Session/payment storage |
| **Printing** | QPrinter + win32print | stdlib + pywin32 | Windows print spooler |
| **USB Detection** | psutil | Latest | Removable drive detection |
| **Configuration** | JSON | stdlib | App settings |
| **Packaging** | PyInstaller | Latest | Standalone .exe build |

### Inter-Component Communication

**Pattern**: Qt Signals & Slots (observer pattern)

```python
# Example signal flow
Operator Window --[live_view_updated(bytes)]--> Viewer Window
Operator Window --[countdown_started(int)]----> Viewer Window
Operator Window --[photo_captured(str)]-------> Viewer Window
Operator Window --[final_composite_ready(str)]> Viewer Window
Operator Window --[session_ended()]-----------> Viewer Window
```

---

## 6. Core Features

### 6.1 Camera Integration

#### 6.1.1 Camera Detection & Connection

**Priority**: CRITICAL  
**Requirements**:
- Auto-detect Canon EOS DSLR via USB on startup
- Fallback to OpenCV webcam if no DSLR found
- Support IP camera via RTSP stream (DroidCam, EpocCam)
- Show connection status badge (green/red)
- Auto-reconnect on disconnect (within 30 seconds)

**Implementation**:
```python
# Detection order:
1. digiCamControl REST API (localhost:5513)
2. OpenCV direct USB capture (enumerate devices 0-9)
3. RTSP stream URL (if configured)
```

**Status Indicators**:
- 🟢 Green: Connected and ready
- 🟡 Yellow: Connecting/reconnecting
- 🔴 Red: Disconnected/error

#### 6.1.2 Live View Stream

**Priority**: CRITICAL  
**Requirements**:
- Real-time camera feed at **15+ fps**
- Stream to both Operator and Viewer dashboards
- JPEG encoding (quality: 85) for performance
- Run in dedicated QThread (never block main UI)
- Scale to display size before rendering

**Performance Targets**:
- Frame rate: 15-30 fps (configurable)
- Latency: < 100ms
- CPU usage: < 20% on low-end PC

#### 6.1.3 Tethered Capture

**Priority**: CRITICAL  
**Requirements**:
- Trigger full-resolution capture from software
- Download JPEG Large/Fine to `events/[EventName]/raw/`
- Support manual mode (button click) and auto mode (countdown)
- Save camera metadata (ISO, aperture, shutter speed)

**Capture Flow**:
```
1. Trigger (button or countdown)
2. Camera captures full-res image
3. Download to raw/ folder (< 2 seconds)
4. Emit signal to compositor
5. Continue to next shot
```

---

### 6.2 Frame Template System

#### 6.2.1 Frame Requirements

**Format**: PNG with RGBA transparency (alpha channel required)  
**Dimensions**: Match print size at 300 DPI  
**Maximum Slots**: 4 photo slots per frame  
**Naming Convention**: `[EventCode]_[FrameName]_[Slots]slot.png`

**Supported Print Sizes**:

| Size | Pixels @ 300 DPI | Aspect Ratio | Use Case |
|------|-----------------|--------------|----------|
| 4" x 6" | 1200 x 1800 | 2:3 | Standard event print |
| 6" x 8" | 1800 x 2400 | 3:4 | Larger keepsake |
| 5" x 7" | 1500 x 2100 | 5:7 | Portrait style |
| 4" x 4" | 1200 x 1200 | 1:1 | Square/Instagram |
| Custom | Operator-defined | Any | Special events |

#### 6.2.2 Frame JSON Metadata

**Required Fields**:
```json
{
  "frame_name": "BlueFloral",
  "print_size": "4x6",
  "output_dpi": 300,
  "slots": [
    {
      "id": 1,
      "x_pct": 5.0,
      "y_pct": 8.0,
      "w_pct": 90.0,
      "h_pct": 42.0,
      "fit": "fill"  // "fill" | "fit" | "stretch"
    },
    {
      "id": 2,
      "x_pct": 5.0,
      "y_pct": 52.0,
      "w_pct": 90.0,
      "h_pct": 42.0,
      "fit": "fill"
    }
  ]
}
```

**Field Descriptions**:
- `x_pct`, `y_pct`: Position as percentage of frame dimensions (0-100)
- `w_pct`, `h_pct`: Size as percentage of frame dimensions (0-100)
- `fit`: How to place photo in slot
  - `"fill"`: Crop to fill (default, best for portraits)
  - `"fit"`: Letterbox, maintain aspect ratio
  - `"stretch"`: Stretch to fit (not recommended)

#### 6.2.3 Frame Management Features

**CRUD Operations**:
- ✅ **Create**: Upload PNG + JSON to `/frames/[EventCode]/`
- ✅ **Read**: Display as thumbnail grid in operator UI
- ✅ **Update**: Edit frame name, replace image, update JSON
- ✅ **Delete**: Remove from database and filesystem

**Validation**:
- Check PNG has RGBA mode (alpha channel)
- Verify JSON structure matches schema
- Validate slot positions within bounds (0-100%)
- Warn if dimensions don't match standard print sizes

---

### 6.3 Session & Capture Workflow

#### 6.3.1 Complete Session Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. EVENT SETUP                                              │
│     ├─ Create event (name, date, venue)                     │
│     ├─ Auto-create folder: events/[Name_Date]/              │
│     └─ Load frames for event                                │
│                                                               │
│  2. FRAME SELECTION                                          │
│     ├─ Operator clicks frame thumbnail                      │
│     ├─ Frame overlay appears on live preview                │
│     └─ Viewer sees framed preview                           │
│                                                               │
│  3. CLIENT ENTRY                                             │
│     ├─ Enter client name (optional)                         │
│     ├─ Create session record in database                    │
│     └─ Show shot counter: "Shot 1 of 2"                     │
│                                                               │
│  4. CAPTURE PHASE (repeat for each slot)                    │
│     ├─ Show live preview with frame overlay                 │
│     ├─ Start countdown (3-10 seconds, configurable)         │
│     ├─ Large "SMILE!" animation                             │
│     ├─ Trigger capture                                      │
│     ├─ Download photo to raw/ folder                        │
│     ├─ Show captured photo for 3-second review              │
│     ├─ Return to live preview                               │
│     └─ Increment shot counter                               │
│                                                               │
│  5. COMPOSITING                                              │
│     ├─ All shots captured                                   │
│     ├─ Place photos into frame slots                        │
│     ├─ Save composite to output/ folder (< 3 seconds)       │
│     └─ Update session record with output path               │
│                                                               │
│  6. DELIVERY                                                 │
│     ├─ Show final photo on Viewer dashboard                 │
│     ├─ Print dialog (quantity, preview)                     │
│     ├─ USB export prompt (if drive detected)                │
│     └─ Session complete                                     │
│                                                               │
│  7. LOGGING                                                  │
│     ├─ Record payment amount                                │
│     ├─ Mark payment status (Paid/Unpaid/Complimentary)      │
│     └─ Add to session log table                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### 6.3.2 Capture Modes

**Mode 1: Auto-Countdown**
- Configurable countdown: 3, 5, 7, or 10 seconds
- Visual countdown overlay (large numbers)
- Audio beep on final 3 seconds (optional)
- Auto-trigger at zero

**Mode 2: Manual Trigger**
- Operator presses large "CAPTURE" button
- No countdown, immediate capture
- Useful for group photos, kids, pets
- Keyboard shortcut: Spacebar

#### 6.3.3 Shot Management

**Multi-Shot Sessions**:
- Frame defines number of slots (1-4)
- UI shows: "Shot X of Y"
- Can retake last shot before compositing
- Retake replaces photo in that slot
- All raw photos preserved in `raw/` folder

---

### 6.4 Session & Payment Tracking

#### 6.4.1 Database Schema

**SQLite Database**: `snapframe.db` (auto-created on first run)

```sql
-- Events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    venue TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Frames table
CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    json_path TEXT NOT NULL,
    slots INTEGER DEFAULT 1,
    print_size_w INTEGER,
    print_size_h INTEGER,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    frame_id INTEGER NOT NULL,
    client_name TEXT,
    amount_paid REAL DEFAULT 0.0,
    payment_status TEXT DEFAULT 'Unpaid',  -- Paid | Unpaid | Complimentary
    output_file_path TEXT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    printed_at TIMESTAMP,
    usb_exported_at TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (frame_id) REFERENCES frames(id) ON DELETE CASCADE
);

-- Photos table (individual raw shots)
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    slot_index INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

#### 6.4.2 Session Log Features

**Table Columns**:
1. ID (session number)
2. Client Name
3. Frame Name
4. Photo (thumbnail preview, 68x68px)
5. Shots (count: e.g., "2/2")
6. Payment (amount: ₱500.00)
7. Status (Paid/Unpaid/Complimentary - color coded)
8. Time (HH:MM:SS)
9. Actions (Edit ✏️ | Delete 🗑️ buttons)

**Row Styling**:
- Height: 60px
- Alternating backgrounds: `#1a1a1a` / `#222222`
- Gold accent on selection: `#D4AF37`
- Status colors: Green (Paid), Yellow (Unpaid), Red (Complimentary)

**Session Log Actions**:
- ✅ Edit session (client name, payment amount)
- ✅ Delete session (with confirmation, cascades to files)
- ✅ Reprint photo (right-click context menu)
- ✅ View photo in file explorer

#### 6.4.3 Reporting & Export

**Daily Summary** (to implement):
- Total sessions today
- Total revenue today
- Most popular frame
- Average payment amount

**CSV Export** (to implement):
- Export all sessions for an event
- Fields: ID, Client, Frame, Amount, Status, Timestamp, Output Path
- Filename: `sessions_[EventName]_[Date].csv`

---

### 6.5 Print Management

#### 6.5.1 Printer Configuration

**Default Printer**: Saved in `config.json`  
**Supported**: Epson standard printers (primary), any Windows printer  
**Print Quality**: 300 DPI minimum

**Printer Selection**:
- First run: Dialog to select from installed printers
- Save selection to config
- Changeable in settings anytime

#### 6.5.2 Print Dialog

**Components**:
- Thumbnail preview of final composite
- Quantity selector (1-5 copies, default: 1)
- Paper size dropdown (match frame size)
- Print button (sends to printer)
- Skip button (closes dialog)

**Print Workflow**:
```
1. User clicks "Print" after compositing
2. Print dialog opens with preview
3. Select quantity (default 1)
4. Click "Print"
5. Send to printer via QPrinter/win32print
6. Log printed_at timestamp in database
7. Show success notification
```

#### 6.5.3 Auto-Print Mode

**Optional Feature**: Skip dialog, print immediately
- Configurable in settings
- Quantity: 1 copy
- Paper size: Match frame
- Useful for high-volume events

---

### 6.6 USB Export

#### 6.6.1 Drive Detection

**Method**: Use `psutil.disk_partitions()` to detect removable drives  
**Timing**: Scan on app launch + monitor for new drives  
**Filter**: Only show USB drives (exclude C:, DVD, network drives)

**Detection Logic**:
```python
import psutil

def get_usb_drives():
    usb_drives = []
    for partition in psutil.disk_partitions(all=False):
        if 'removable' in partition.opts.lower():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                usb_drives.append({
                    'drive_letter': partition.mountpoint,
                    'free_space_gb': usage.free / (1024**3),
                    'total_space_gb': usage.total / (1024**3)
                })
            except:
                pass
    return usb_drives
```

#### 6.6.2 Export Workflow

```
1. After compositing, scan for USB drives
2. If found: Show export prompt
   - "Save to USB drive (E:)"
   - Show free space: "45.2 GB available"
3. User clicks "Export"
4. Copy composite JPEG to USB root
5. Show progress bar
6. Show success toast: "Photo saved to USB!"
7. Update database: usb_exported_at = NOW()
8. Viewer dashboard shows confirmation overlay
```

**Error Handling**:
- No USB drive: Skip silently (no error shown)
- USB full: Show error, offer retry
- Write-protected: Show error, offer retry
- Copy failed: Show error with details

---

## 7. UI/UX Specifications

### 7.1 Dual-Window Architecture

#### Window 1: Operator Dashboard

**Type**: QMainWindow (full-screen capable)  
**Purpose**: Main control center for photographer  
**Position**: Primary monitor

**Layout** (5 panels):

```
┌─────────────────────────────────────────────────────────────┐
│  TOP BAR (70px height)                                      │
│  📸 SnapFrame Pro | Event: Wedding 2026 | 🟢 Connected      │
│  Session #45 | ⚙️ | 🌙 | ✏️ Edit Event | 🗑️ Delete Event   │
├──────────┬────────────────────────────────────┬─────────────┤
│          │                                    │             │
│ LEFT     │         CENTER PANEL               │   RIGHT     │
│ PANEL    │         (Live Preview)             │   PANEL     │
│ (Frames) │                                    │  (Session)  │
│          │     ┌──────────────────────┐       │             │
│ Frame    │     │                      │       │ Client:     │
│ Thumbs   │     │   Camera Feed        │       │ [Input]     │
│ (Grid)   │     │   + Frame Overlay    │       │             │
│          │     │                      │       │ Shots:      │
│ [Thumb1] │     │   [Countdown]        │       │ 1 of 2      │
│ [Thumb2] │     │                      │       │             │
│ [Thumb3] │     └──────────────────────┘       │ [CAPTURE]   │
│          │                                    │ [Retake]    │
│          │                                    │             │
│          │                                    │ [Print]     │
│          │                                    │ [USB]       │
├──────────┴────────────────────────────────────┴─────────────┤
│  BOTTOM BAR (Session Log Table)                              │
│  ID | Client | Frame | Photo | Shots | Payment | Status | Actions │
│  1  | John   | Floral| [🖼️] | 2/2   | ₱500   | Paid   | ✏️ 🗑️   │
│  2  | Sarah  | Classic│[🖼️]| 1/2   | ₱500   | Unpaid | ✏️ 🗑️   │
└─────────────────────────────────────────────────────────────┘
```

#### Window 2: Viewer Dashboard

**Type**: QWidget (frameless, full-screen)  
**Purpose**: Client-facing display on second monitor  
**Position**: Secondary monitor (auto-detected)

**States**:
1. **Idle Screen**: Branded slideshow or logo
2. **Live Preview**: Camera feed + frame overlay
3. **Countdown**: Large animated numbers (5...4...3...2...1...SMILE!)
4. **Capture Flash**: Brief white flash animation
5. **Review**: Show captured photo for 3 seconds
6. **Final Result**: Display composited image full-screen

---

### 7.2 Theme System

#### Dark Mode (Default)

**Color Palette**:
```
Background: #0a0a0a (main), #1a1a1a (panels), #2d2d2d (widgets)
Gold Accent: #FFD700 (primary), #D4AF37 (secondary)
Text: #ffffff (primary), #cccccc (secondary)
Status Green: #48bb78
Status Red: #f56565
Status Yellow: #ffd700
Borders: #D4AF37 (gold)
```

**Button Styling**:
```css
/* Primary Buttons */
QPushButton {
    background-color: #2d2d2d;
    color: #FFD700;
    border: 2px solid #D4AF37;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #D4AF37;
    color: #000000;
}
QPushButton:pressed {
    background-color: #FFD700;
}

/* Danger Buttons (Delete) */
QPushButton.danger {
    background-color: #e74c3c;
    border: 2px solid #c0392b;
    color: white;
}
QPushButton.danger:hover {
    background-color: #c0392b;
}
```

**Table Styling**:
```css
QTableWidget {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 2px solid #D4AF37;
    border-radius: 8px;
    gridline-color: #2d2d2d;
}
QHeaderView::section {
    background-color: #2d2d2d;
    color: #FFD700;
    padding: 8px;
    border-bottom: 2px solid #D4AF37;
    font-weight: bold;
}
QTableWidget::item:selected {
    background-color: #D4AF37;
    color: #000000;
}
QTableWidget::item:nth-of-type(even) {
    background-color: #222222;
}
```

#### Light Mode

**Color Palette**:
```
Background: #ffffff (main), #f5f5f5 (panels), #e0e0e0 (widgets)
Gold Accent: #D4AF37 (primary), #C9A84C (secondary)
Text: #000000 (primary), #333333 (secondary)
```

**Toggle**: Moon 🌙 / Sun ☀️ icon in top bar

---

### 7.3 Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Space` | Trigger capture | When not in countdown |
| `Ctrl+Z` | Retake last shot | During active session |
| `Ctrl+P` | Print current photo | After compositing |
| `Ctrl+N` | New client session | Anytime |
| `Ctrl+M` | Toggle capture mode | Anytime |
| `Ctrl+S` | Open settings | Anytime |
| `Esc` | Cancel countdown | During countdown |

---

## 8. Performance Requirements

### 8.1 Target Metrics

| Metric | Target | Low-End PC Target | Measurement |
|--------|--------|-------------------|-------------|
| **App Startup** | < 10 seconds | < 15 seconds | Launch to first live frame |
| **Live View FPS** | 15-30 fps | 15 fps minimum | Frames per second |
| **Compositing Time** | < 3 seconds | < 5 seconds | Capture to final image |
| **UI Responsiveness** | 60 fps | 30 fps | UI thread frame rate |
| **Memory Usage** | < 500 MB | < 700 MB | After 50 sessions |
| **Disk Space** | ~10 MB per session | Same | Photos + database |
| **CPU Usage** | < 20% | < 40% | During active capture |

### 8.2 Low-End PC Optimizations

**CRITICAL for smooth operation on budget hardware**:

#### 8.2.1 Live View Optimizations

```python
# 1. Frame Skipping (reduce processing by 50%)
if frame_count % 2 == 0:  # Process every other frame
    update_preview(frame)

# 2. Lower Resolution for Preview
preview_frame = cv2.resize(frame, (640, 480))  # Not full HD

# 3. JPEG Compression for IPC
jpeg_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])[1]

# 4. UI Update Throttling
if time.time() - last_update < 0.066:  # Max 15 updates/sec
    return
```

#### 8.2.2 Compositing Optimizations

```python
# 1. Pre-cache frames at session start
self.cached_frame = frame_image.resize((width, height), Image.BILINEAR)

# 2. Use BILINEAR for preview, LANCZOS only for final
photo.thumbnail(slot_size, Image.BILINEAR)  # Fast
final_composite.resize((width, height), Image.LANCZOS)  # High quality

# 3. Release memory immediately
del photo, frame_image
import gc; gc.collect()

# 4. Run in background thread
compositor_thread = Thread(target=composite_and_save)
compositor_thread.start()
```

#### 8.2.3 UI Optimizations

```python
# 1. Lazy loading (defer non-critical)
QTimer.singleShot(100, self.load_events)  # Load after UI shows

# 2. Disable animations on low-end
app.setStyle('Fusion')  # Simpler than native styles

# 3. Use FastTransformation for thumbnails
pixmap.scaled(size, Qt.KeepAspectRatio, Qt.FastTransformation)

# 4. Throttle heavy updates
if time.time() - last_update < 0.1:  # 10 updates/sec max
    return
```

#### 8.2.4 Database Optimizations

```python
# 1. Enable WAL mode (better concurrent performance)
cursor.execute("PRAGMA journal_mode=WAL;")

# 2. Batch inserts for multiple photos
cursor.executemany(
    "INSERT INTO photos (session_id, slot_index, file_path) VALUES (?, ?, ?)",
    photo_records
)

# 3. Use transactions
cursor.execute("BEGIN TRANSACTION;")
# ... multiple operations ...
conn.commit()
```

#### 8.2.5 Memory Management

```python
# 1. Limit photo cache
self.recent_photos = self.recent_photos[-10:]  # Keep last 10

# 2. Clear large objects after use
del large_image
import gc; gc.collect()

# 3. Use generators instead of lists
def read_photos():
    for path in photo_paths:
        yield load_photo(path)  # Lazy loading
```

### 8.3 Startup Time Optimization

**Target**: < 10 seconds to first live frame (SSD), < 15 seconds (HDD)

**Deferred Loading Strategy**:
```python
def __init__(self):
    # 1. Minimal UI setup (2 seconds)
    setup_basic_ui()
    self.show()
    
    # 2. Camera init (runs while UI is visible)
    QTimer.singleShot(100, self.initialize_camera)
    
    # 3. Load events (deferred 500ms)
    QTimer.singleShot(500, self.load_events)
    
    # 4. Load session history (deferred 1 second)
    QTimer.singleShot(1000, self.load_session_history)
    
    # 5. Load heavy modules on demand
    # from PyQt6.QtPrintSupport import QPrinter  # Import when needed
```

**Non-Critical Imports** (defer until first use):
- `win32print` (only when printing)
- `psutil` (only when USB export)
- `pandas` (only when CSV export)

---

## 9. Database Schema

### 9.1 Complete Schema

```sql
-- Enable WAL mode for better performance
PRAGMA journal_mode=WAL;

-- Events
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    venue TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Frames
CREATE TABLE IF NOT EXISTS frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    json_path TEXT NOT NULL,
    slots INTEGER DEFAULT 1,
    print_size_w INTEGER,
    print_size_h INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    frame_id INTEGER NOT NULL,
    client_name TEXT,
    amount_paid REAL DEFAULT 0.0,
    payment_status TEXT DEFAULT 'Unpaid',
    output_file_path TEXT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    printed_at TIMESTAMP,
    usb_exported_at TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (frame_id) REFERENCES frames(id) ON DELETE CASCADE
);

-- Photos (individual shots)
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    slot_index INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_sessions_event ON sessions(event_id);
CREATE INDEX idx_sessions_frame ON sessions(frame_id);
CREATE INDEX idx_photos_session ON photos(session_id);
CREATE INDEX idx_frames_event ON frames(event_id);
```

### 9.2 Common Queries

```sql
-- Get all sessions for an event
SELECT s.*, f.name as frame_name 
FROM sessions s
JOIN frames f ON s.frame_id = f.id
WHERE s.event_id = ?
ORDER BY s.captured_at DESC;

-- Daily summary
SELECT 
    COUNT(*) as total_sessions,
    SUM(amount_paid) as total_revenue,
    AVG(amount_paid) as avg_payment
FROM sessions
WHERE DATE(captured_at) = DATE('now');

-- Most popular frame
SELECT f.name, COUNT(s.id) as usage_count
FROM frames f
JOIN sessions s ON f.id = s.frame_id
WHERE s.event_id = ?
GROUP BY f.id
ORDER BY usage_count DESC
LIMIT 1;
```

---

## 10. File Structure

```
AIraPhotobooth/
│
├── main.py                          # App entry point
├── config.json                      # Global settings
├── config.py                        # Config management class
├── requirements.txt                 # Python dependencies
├── snapframe.db                     # SQLite database (auto-created)
│
├── core/
│   ├── __init__.py
│   ├── camera.py                    # Camera detection, live view, capture
│   ├── compositor.py                # Frame + photo compositing (Pillow)
│   ├── session_manager.py           # Database CRUD operations
│   ├── print_manager.py             # Print job dispatch
│   ├── usb_exporter.py              # USB drive detection + file copy
│   ├── frame_loader.py              # Load/validate frame PNG + JSON
│   └── recovery_manager.py          # Crash recovery state save/restore
│
├── ui/
│   ├── __init__.py
│   ├── operator_window.py           # Main operator dashboard
│   ├── viewer_window.py             # Client-facing viewer window
│   ├── frame_selector.py            # Thumbnail grid widget
│   ├── countdown_overlay.py         # Animated countdown widget
│   ├── session_log_table.py         # Session history table
│   ├── print_dialog.py              # Print confirmation dialog
│   └── usb_dialog.py                # USB export prompt dialog
│
├── frames/                          # Frame templates storage
│   └── [EventCode]/
│       ├── Frame1_2slot.png
│       ├── Frame1_2slot.json
│       ├── Frame2_1slot.png
│       └── Frame2_1slot.json
│
├── events/                          # Per-event auto-created folders
│   └── [EventName_Date]/
│       ├── raw/                     # Downloaded camera JPEGs
│       └── output/                  # Final composited photos
│
├── assets/
│   ├── icons/
│   │   ├── icon_capture.png
│   │   ├── icon_print.png
│   │   └── icon_usb.png
│   ├── fonts/
│   └── idle_slides/                 # Viewer idle screen images
│
└── backups/                         # Daily database backups
    └── snapframe_YYYYMMDD.db
```

---

## 11. Development Phases

### Phase 0: Setup & Environment (1 week)
- [x] Python 3.11+ environment setup
- [x] PyQt6 skeleton with dual windows
- [x] digiCamControl test on Windows
- [x] Basic config.json system

### Phase 1: Camera Module (1 week)
- [x] Camera detection (DSLR, webcam, IP)
- [x] Live view stream (15+ fps)
- [x] Tethered capture
- [x] Auto-reconnect on disconnect

### Phase 2: Frame Compositor (1 week)
- [x] PNG frame loading with alpha
- [x] JSON slot parser
- [x] Photo placement (fill/fit/stretch)
- [x] Frame caching system

### Phase 3: Operator Dashboard (2 weeks)
- [x] Full UI layout (5 panels)
- [x] Frame selector with thumbnails
- [x] Capture flow (countdown + manual)
- [x] Session panel with controls
- [x] Print dialog

### Phase 4: Viewer Dashboard (1 week)
- [x] Second-screen window
- [x] Live preview with frame overlay
- [x] Countdown animation
- [x] Final result display
- [ ] Idle/attract screen

### Phase 5: Session & Payment DB (1 week)
- [x] SQLite schema + CRUD
- [x] Session log table UI
- [x] Payment tracking
- [x] Edit/Delete sessions
- [ ] CSV export
- [ ] Daily summary stats

### Phase 6: Print + USB Export (4 days)
- [x] Print dialog
- [ ] Auto-print mode
- [ ] win32print integration
- [ ] USB drive detection (psutil)
- [ ] USB export workflow
- [ ] Progress indicator

### Phase 7: Testing & Polish (1 week)
- [ ] End-to-end event simulation (100+ sessions)
- [ ] Performance profiling
- [ ] Memory leak testing
- [ ] Bug fixes
- [ ] Low-end PC optimization testing

### Phase 8: Packaging (3 days)
- [ ] PyInstaller .exe build
- [ ] README documentation
- [ ] User guide PDF
- [ ] Installer script (optional)

**Total Estimated Time**: 10-11 weeks (part-time solo developer)

---

## 12. Risk Management

| Risk | Likelihood | Impact | Mitigation Strategy | Status |
|------|-----------|--------|---------------------|--------|
| **digiCamControl Windows support** | High | Critical | Use as primary Canon backend, test in Phase 0 | ✅ Mitigated |
| **Camera disconnect mid-event** | Medium | High | Auto-reconnect loop (<30s), session state saved after each capture | ✅ Implemented |
| **Frame PNG alpha composite issue** | Low | High | Validate on import, warn if not RGBA mode | ✅ Implemented |
| **Compositing lag on slow PC** | Low | Medium | Pre-cache frames, background thread, BILINEAR for preview | ✅ Optimized |
| **Epson driver incompatibility** | Low | Medium | QPrinter primary, win32print fallback | ⏳ Partial |
| **UI freezing on low-end hardware** | Medium | Medium | All I/O in worker threads, profile in Phase 7 | ✅ Optimized |
| **USB drive full/write-protected** | Medium | Low | Check free space before copy, show clear error | ⏳ Not implemented |
| **Database corruption** | Low | High | WAL mode, daily backups, transaction safety | ⏳ WAL not enabled |

---

## 13. Implementation Status

### ✅ Fully Implemented (90% Complete)

| Feature | Status | Notes |
|---------|--------|-------|
| Dual-window architecture | ✅ Complete | Operator + Viewer dashboards |
| Camera detection | ✅ Complete | DSLR + webcam with friendly names |
| Live preview | ✅ Complete | 15 fps with optimizations |
| Frame overlay | ✅ Complete | KeepAspectRatio, no stretching |
| Countdown capture | ✅ Complete | Configurable duration |
| Auto-compositing | ✅ Complete | < 3 seconds with Pillow |
| Event CRUD | ✅ Complete | Create, edit, delete events |
| Frame CRUD | ✅ Complete | Upload, edit name, delete |
| Session CRUD | ✅ Complete | Create, edit, delete sessions |
| Session log table | ✅ Complete | Professional black/gold theme |
| Print dialog | ✅ Complete | Preview + quantity selector |
| Dark/Light theme | ✅ Complete | Toggle in top bar |
| Performance optimizations | ✅ Complete | Frame skipping, throttling |
| Crash recovery | ✅ Complete | Auto-save session state |

### ⏳ Not Yet Implemented (10% Remaining)

| Feature | Priority | Effort | Notes |
|---------|----------|--------|-------|
| USB export | HIGH | 2-3 days | psutil detection + copy |
| CSV export | MEDIUM | 1 day | Session report to file |
| Daily summary stats | MEDIUM | 1 day | Revenue, session count |
| Auto-print mode | MEDIUM | 0.5 day | Skip dialog, print immediately |
| Idle/attract screen | LOW | 1-2 days | Branded slideshow for viewer |
| Event name watermark | LOW | 0.5 day | Overlay on viewer dashboard |
| SQLite WAL mode | MEDIUM | 0.5 day | Enable for better performance |
| Camera settings UI | LOW | 1-2 days | ISO, aperture, shutter controls |
| Payment status tracking | MEDIUM | 0.5 day | Paid/Unpaid/Complimentary |
| Print queue management | LOW | 1 day | Show queue status |

---

## 14. Future Roadmap

### Version 2.0 (Planned Enhancements)

**Photo Filters & Effects**:
- Basic filters: B&W, Vintage, Warm tone
- Apply via Pillow `ImageFilter` before compositing
- Filter preview strip in operator dashboard
- Real-time preview on live feed

**Beauty / Skin Smoothing Mode**:
- OpenCV bilateral filter on face regions
- Face detection via OpenCV Haar cascades
- Adjustable intensity slider
- Toggle on/off per session

**GIF / Boomerang Mode**:
- Capture burst of 4-6 frames
- Export as animated GIF using Pillow
- Configurable delay between frames
- Reverse playback (boomerang effect)

**Multi-Language UI**:
- Qt translation files (`.ts`)
- Filipino (Tagalog) support
- Spanish, Chinese, Japanese
- Language selector in settings

### Version 3.0 (Advanced Features)

**QR Code Digital Delivery**:
- Generate per-session QR code
- Link to locally hosted Flask file server
- Guests scan with phone to download
- No internet required (same Wi-Fi)

**Cloud Backup**:
- End-of-event upload to Google Drive/Dropbox
- Automatic backup after each session
- Configurable cloud provider
- Encrypted transfer

**Analytics Dashboard**:
- Session trends over time
- Peak hours analysis
- Revenue tracking with charts
- Export to Excel

**Multi-Booth Support**:
- Control multiple photobooths from one app
- Network synchronization
- Centralized session logging
- Load balancing

---

## 📊 Key Performance Indicators (KPIs)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Sessions per hour | 12-15 (4 min/session) | Session log timestamp analysis |
| Compositing time | < 3 seconds | Timer in compositor |
| App startup time | < 10 seconds (SSD) | Stopwatch on launch |
| Crash rate | < 1% of sessions | Recovery manager logs |
| Customer satisfaction | > 90% positive | Post-event survey |
| Print success rate | > 95% | Print manager logs |
| USB export success | > 90% | Export logs |

---

## 📝 Notes for AI Agents

### When Implementing Features:

1. **Always prioritize performance on low-end hardware**:
   - Use frame skipping, throttling, lazy loading
   - Run all I/O in background threads
   - Release memory aggressively

2. **Follow the existing architecture**:
   - PyQt6 signals/slots for inter-window communication
   - Separate core logic from UI
   - Use configuration management via `config.py`

3. **Maintain the black/gold theme**:
   - Dark mode: `#0a0a0a`, `#1a1a1a`, `#FFD700`, `#D4AF37`
   - Light mode: `#ffffff`, `#f5f5f5`, `#D4AF37`
   - Consistent button styling throughout

4. **Database best practices**:
   - Use parameterized queries (prevent SQL injection)
   - Enable WAL mode for performance
   - Batch operations when possible
   - Always use transactions for multiple writes

5. **Error handling**:
   - Show user-friendly error messages
   - Log technical details for debugging
   - Graceful degradation (e.g., USB export fails silently)
   - Never crash the app on recoverable errors

6. **Testing considerations**:
   - Test with 100+ sessions for memory leaks
   - Test on low-end PC (4GB RAM, dual-core CPU)
   - Test with multiple camera types
   - Test frame edge cases (wrong format, missing JSON)

### Code Style Guidelines:

```python
# Use type hints
def composite_photos(self, photos: list[str], frame_path: str) -> str:
    """Composite photos into frame and save.
    
    Args:
        photos: List of photo file paths
        frame_path: Path to frame PNG
        
    Returns:
        Path to saved composite image
    """
    
# Use logging, not print
import logging
logger = logging.getLogger(__name__)
logger.info(f"Session {session_id} created")
logger.error(f"Failed to load frame: {e}")

# Use context managers for files
with open(json_path, 'r') as f:
    metadata = json.load(f)
```

---

## 🎯 Success Criteria

The project is successful when:

1. ✅ **Photographer can run a 200-guest event solo** without manual file management
2. ✅ **Session time reduced from 5-10 minutes to < 2 minutes**
3. ✅ **Zero Photoshop required** - all automation handled by software
4. ✅ **Professional results** - consistent, high-quality composites
5. ✅ **Reliable performance** - no crashes during events
6. ✅ **Smooth on low-end hardware** - runs on budget laptops
7. ✅ **Complete session tracking** - all data logged, exportable
8. ✅ **Client satisfaction** - live preview, fast delivery

---

**Document Version**: 2.1 (AI-Optimized)  
**Last Updated**: April 2026  
**Maintained By**: Development Team  
**Status**: Implementation 90% Complete
