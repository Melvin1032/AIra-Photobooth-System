"""
SnapFrame Pro - Session Manager
Handles database operations for events, sessions, and photos.
"""

import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages photobooth sessions and database operations."""
    
    def __init__(self, db_path: str = "snapframe.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better performance
        self._enable_wal_mode()
        
        # Create tables
        self._create_tables()
        
        logger.info(f"SessionManager initialized: {db_path}")
    
    def _enable_wal_mode(self):
        """Enable SQLite WAL mode for better concurrency."""
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute("PRAGMA cache_size=2000")
            self.conn.execute("PRAGMA temp_store=MEMORY")
            logger.info("SQLite WAL mode enabled")
        except Exception as e:
            logger.error(f"Failed to enable WAL mode: {e}")
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                venue TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Frames table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                slots INTEGER DEFAULT 1,
                price REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                client_name TEXT,
                frame_id INTEGER,
                amount REAL DEFAULT 0,
                payment_status TEXT DEFAULT 'Unpaid',
                shots_taken INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id),
                FOREIGN KEY (frame_id) REFERENCES frames(id)
            )
        ''')
        
        # Photos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                slot_number INTEGER NOT NULL,
                raw_path TEXT,
                processed_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        self.conn.commit()
        logger.info("Database tables created")
    
    # === Event Operations ===
    
    def create_event(self, name: str, date: str, venue: str = "") -> int:
        """Create a new event."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO events (name, date, venue) VALUES (?, ?, ?)",
            (name, date, venue)
        )
        self.conn.commit()
        event_id = cursor.lastrowid
        logger.info(f"Event created: {name} (ID: {event_id})")
        return event_id
    
    def get_event(self, event_id: int) -> Optional[Dict]:
        """Get event by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_events(self) -> List[Dict]:
        """Get all events."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY date DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_event(self, event_id: int, **kwargs):
        """Update event fields."""
        allowed_fields = ['name', 'date', 'venue']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
            values = list(updates.values()) + [event_id]
            
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE events SET {set_clause} WHERE id = ?",
                values
            )
            self.conn.commit()
            logger.info(f"Event {event_id} updated: {updates}")
    
    def delete_event(self, event_id: int):
        """Delete event and all related data."""
        cursor = self.conn.cursor()
        
        # Delete related photos
        cursor.execute('''
            DELETE FROM photos WHERE session_id IN 
            (SELECT id FROM sessions WHERE event_id = ?)
        ''', (event_id,))
        
        # Delete related sessions
        cursor.execute("DELETE FROM sessions WHERE event_id = ?", (event_id,))
        
        # Delete related frames
        cursor.execute("DELETE FROM frames WHERE event_id = ?", (event_id,))
        
        # Delete event
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        
        self.conn.commit()
        logger.info(f"Event {event_id} deleted")
    
    # === Frame Operations ===
    
    def add_frame(self, event_id: int, name: str, image_path: str, 
                  slots: int = 1, price: float = 0) -> int:
        """Add a frame to an event."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO frames (event_id, name, image_path, slots, price) VALUES (?, ?, ?, ?, ?)",
            (event_id, name, image_path, slots, price)
        )
        self.conn.commit()
        frame_id = cursor.lastrowid
        logger.info(f"Frame added: {name} (ID: {frame_id})")
        return frame_id
    
    def get_frames_for_event(self, event_id: int) -> List[Dict]:
        """Get all frames for an event."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM frames WHERE event_id = ? ORDER BY id",
            (event_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def update_frame(self, frame_id: int, **kwargs):
        """Update frame fields."""
        allowed_fields = ['name', 'image_path', 'slots', 'price']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
            values = list(updates.values()) + [frame_id]
            
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE frames SET {set_clause} WHERE id = ?",
                values
            )
            self.conn.commit()
    
    def delete_frame(self, frame_id: int):
        """Delete a frame."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM frames WHERE id = ?", (frame_id,))
        self.conn.commit()
        logger.info(f"Frame {frame_id} deleted")
    
    # === Session Operations ===
    
    def create_session(self, event_id: int, client_name: str = "", 
                       frame_id: int = None) -> int:
        """Create a new session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (event_id, client_name, frame_id) VALUES (?, ?, ?)",
            (event_id, client_name, frame_id)
        )
        self.conn.commit()
        session_id = cursor.lastrowid
        logger.info(f"Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: int) -> Optional[Dict]:
        """Get session by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_sessions_for_event(self, event_id: int) -> List[Dict]:
        """Get all sessions for an event."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.*, f.name as frame_name 
            FROM sessions s
            LEFT JOIN frames f ON s.frame_id = f.id
            WHERE s.event_id = ?
            ORDER BY s.created_at DESC
        ''', (event_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_session(self, session_id: int, **kwargs):
        """Update session fields."""
        allowed_fields = ['client_name', 'frame_id', 'amount', 
                         'payment_status', 'shots_taken', 'status']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
            values = list(updates.values()) + [session_id]
            
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE sessions SET {set_clause} WHERE id = ?",
                values
            )
            self.conn.commit()
    
    def delete_session(self, session_id: int):
        """Delete a session and its photos."""
        cursor = self.conn.cursor()
        
        # Delete photos
        cursor.execute("DELETE FROM photos WHERE session_id = ?", (session_id,))
        
        # Delete session
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        
        self.conn.commit()
        logger.info(f"Session {session_id} deleted")
    
    # === Photo Operations ===
    
    def add_photo(self, session_id: int, slot_number: int, 
                  raw_path: str = None, processed_path: str = None):
        """Add a photo to a session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO photos (session_id, slot_number, raw_path, processed_path) VALUES (?, ?, ?, ?)",
            (session_id, slot_number, raw_path, processed_path)
        )
        self.conn.commit()
    
    def get_photos_for_session(self, session_id: int) -> List[Dict]:
        """Get all photos for a session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM photos WHERE session_id = ? ORDER BY slot_number",
            (session_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
