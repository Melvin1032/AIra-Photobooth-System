# SnapFrame Pro - Quick Implementation Checklist

Print this and check off each item as you implement it.

---

## 📦 Prerequisites

- [ ] Backup your current codebase
- [ ] Create a new Git branch: `git checkout -b feature/performance-optimizations`
- [ ] Install psutil: `pip install psutil`
- [ ] Open INTEGRATION_GUIDE.md for detailed steps

---

## 1️⃣ SQLite WAL Mode (5 minutes)

- [ ] Open `core/session_manager.py`
- [ ] Add import: `from IMPLEMENTATION_performance_optimizer import PerformanceOptimizer`
- [ ] In `__init__`, after `self.conn = sqlite3.connect(...)`, add:
  ```python
  PerformanceOptimizer.enable_sqlite_wal_mode(self.conn)
  ```
- [ ] Save file
- [ ] Test: Run app, check logs for "SQLite optimizations enabled"
- [ ] Verify: `snapframe.db-wal` file appears in project folder

**Status**: ✅ COMPLETE when WAL file exists

---

## 2️⃣ USB Export (1 hour)

### Copy Files
- [ ] Copy `IMPLEMENTATION_usb_exporter.py` to `core/usb_exporter.py`
- [ ] Rename class imports if needed

### Update operator_window.py
- [ ] Add import: `from core.usb_exporter import USBExporter`
- [ ] In `__init__`, add:
  ```python
  self.usb_exporter = USBExporter()
  self.usb_exporter.export_completed.connect(self.on_usb_export_completed)
  ```
- [ ] Add method `export_to_usb(photo_path)` (see INTEGRATION_GUIDE.md)
- [ ] Add method `on_usb_export_completed(file_path, success, message)`
- [ ] Add USB button to UI (or integrate into existing button)

### Test
- [ ] Insert USB drive
- [ ] Complete a photo session
- [ ] Click USB Export button
- [ ] Verify file appears on USB drive
- [ ] Check logs for "Successfully exported to USB"

**Status**: ✅ COMPLETE when file copies to USB successfully

---

## 3️⃣ CSV Export (1 hour)

### Copy Files
- [ ] Copy `IMPLEMENTATION_csv_export.py` to `core/csv_export.py`

### Update operator_window.py
- [ ] Add import: `from core.csv_export import CSVExporter`
- [ ] Add method `export_sessions_to_csv()`
- [ ] Add method `export_daily_report()`
- [ ] Add Export menu or button to UI

### Test
- [ ] Create 3 test sessions
- [ ] Click "Export CSV"
- [ ] Open exported file in Excel
- [ ] Verify all sessions present with correct data
- [ ] Test daily report export

**Status**: ✅ COMPLETE when CSV opens correctly in Excel

---

## 4️⃣ Daily Summary Statistics (30 minutes)

### Update operator_window.py
- [ ] Add labels for summary display (today_sessions_label, today_revenue_label, popular_frame_label)
- [ ] Add method `update_daily_summary()`
- [ ] Add QTimer to update every 30 seconds:
  ```python
  self.summary_timer = QTimer()
  self.summary_timer.timeout.connect(self.update_daily_summary)
  self.summary_timer.start(30000)
  ```

### Test
- [ ] Create test sessions with different amounts
- [ ] Wait 30 seconds
- [ ] Verify summary shows correct count and revenue
- [ ] Check calculations match database

**Status**: ✅ COMPLETE when summary updates automatically

---

## 5️⃣ Frame Pre-Caching (30 minutes)

### Update compositor.py
- [ ] Add import: `from IMPLEMENTATION_performance_optimizer import PerformanceOptimizer`
- [ ] In `__init__`, add: `self.optimizer = PerformanceOptimizer()`
- [ ] Modify `composite()` method to check cache first:
  ```python
  frame_image = self.optimizer.get_cached_frame(frame_id)
  if frame_image is None:
      frame_image = Image.open(png_path)
  ```

### Update operator_window.py
- [ ] In `on_frame_selected()`, add pre-caching:
  ```python
  self.compositor.optimizer.preload_frame(frame_id, png_path, output_size)
  ```

### Test
- [ ] Select a frame
- [ ] Check logs for "Frame pre-cached"
- [ ] Complete session
- [ ] Verify compositing < 3 seconds
- [ ] Check logs for "Frame cache hit"

**Status**: ✅ COMPLETE when compositing is noticeably faster

---

## 6️⃣ Memory Cleanup (10 minutes)

### Update operator_window.py
- [ ] Import PerformanceOptimizer (if not already done)
- [ ] In `__init__`, add:
  ```python
  self.optimizer = PerformanceOptimizer()
  self.memory_timer = QTimer()
  self.memory_timer.timeout.connect(lambda: self.optimizer.cleanup_memory())
  self.memory_timer.start(60000)  # Every 60 seconds
  ```
- [ ] In session completion method, add:
  ```python
  self.optimizer.cleanup_memory(force=True)
  ```

### Update compositor.py
- [ ] After saving composite, add:
  ```python
  self.optimizer.release_large_objects(frame_image, composite)
  ```

### Test
- [ ] Run app, open Task Manager
- [ ] Monitor memory usage
- [ ] Complete 20+ sessions
- [ ] Verify memory stays under 700 MB
- [ ] Check logs for "Memory cleanup" messages

**Status**: ✅ COMPLETE when memory stays stable over time

---

## 7️⃣ Performance Monitoring (Optional - 15 minutes)

- [ ] Add performance label to UI
- [ ] Add QTimer to update every 10 seconds
- [ ] Display memory usage
- [ ] Add color coding (green/yellow/red)

### Test
- [ ] Verify label shows memory usage
- [ ] Color changes based on usage level

**Status**: ✅ COMPLETE (optional, for debugging)

---

## 🧪 Final Testing

### Integration Tests
- [ ] Complete full session: Frame select → Capture → Composite → Print → USB Export
- [ ] Verify no errors in logs
- [ ] Check all files created (raw, output, USB copy)
- [ ] Export CSV, verify data matches sessions
- [ ] Check daily summary accuracy

### Stress Tests
- [ ] Complete 50 sessions rapidly (simulate busy event)
- [ ] Monitor memory (should stay under 700 MB)
- [ ] Monitor CPU (should stay under 40%)
- [ ] Verify no slowdown over time
- [ ] Check no "database locked" errors

### Low-End PC Tests
- [ ] Run on target low-end hardware (if available)
- [ ] Verify live preview 15+ fps
- [ ] Verify compositing < 5 seconds
- [ ] Verify app startup < 15 seconds
- [ ] Check UI responsiveness

---

## 📊 Success Criteria Checklist

- [ ] ✅ SQLite WAL file exists
- [ ] ✅ USB export works (file appears on USB)
- [ ] ✅ CSV export works (opens in Excel)
- [ ] ✅ Daily summary updates every 30 seconds
- [ ] ✅ Frame caching active (logs show "cache hit")
- [ ] ✅ Memory cleanup runs (logs show cleanup messages)
- [ ] ✅ Memory usage stable after 50 sessions (< 700 MB)
- [ ] ✅ No database lock errors
- [ ] ✅ Compositing < 3 seconds
- [ ] ✅ No crashes or freezes

---

## 🐛 Troubleshooting

### If USB export fails:
- [ ] Check USB drive detected: `usb_exporter.detect_usb_drives()`
- [ ] Check drive not write-protected
- [ ] Check sufficient free space
- [ ] Review logs for error details

### If CSV export empty:
- [ ] Verify event has sessions in database
- [ ] Check SQL query in logs
- [ ] Verify file permissions for output directory

### If memory still high:
- [ ] Verify `release_large_objects()` called after compositing
- [ ] Reduce `cleanup_interval` to 30 seconds
- [ ] Check for unclosed file handles
- [ ] Monitor with Task Manager

### If frame cache not working:
- [ ] Check PNG path is correct
- [ ] Verify PIL installed: `pip install Pillow`
- [ ] Review logs for "preload_frame" calls

---

## 📝 Notes

- [ ] Document any customizations made
- [ ] Note any issues encountered
- [ ] Record performance metrics before/after
- [ ] Update team on implementation status

---

## ✅ Final Sign-Off

**Implemented by**: ___________________  
**Date**: ___________________  
**Tested by**: ___________________  
**Date**: ___________________  

**All optimizations working**: ☐ YES  ☐ NO  
**Performance improved**: ☐ YES  ☐ NO  
**No regressions**: ☐ YES  ☐ NO  

**Comments**:
_____________________________________________
_____________________________________________
_____________________________________________

---

**Need help?**  
- Check `INTEGRATION_GUIDE.md` for detailed steps
- Check `OPTIMIZATION_SUMMARY.md` for overview
- Check `logs/app.log` for error messages
- Review implementation code in `IMPLEMENTATION_*.py` files
