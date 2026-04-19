"""AIra Pro Photobooth System - CSV Export Module
Exports session data to CSV format for reporting and accounting.
Optimized for low-end PCs using built-in csv module (no pandas required).
"""

import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class CSVExporter:
    """Export session data to CSV format."""
    
    def __init__(self, db_connection):
        """
        Initialize CSV exporter.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def export_event_sessions(self, event_id: int, output_dir: Optional[str] = None) -> str:
        """
        Export all sessions for an event to CSV.
        
        Args:
            event_id: Event ID to export
            output_dir: Output directory (default: events/[EventName]/)
            
        Returns:
            Path to exported CSV file
        """
        try:
            cursor = self.db.cursor()
            
            # Get event info
            cursor.execute("SELECT name, date FROM events WHERE id = ?", (event_id,))
            event = cursor.fetchone()
            
            if not event:
                raise ValueError(f"Event {event_id} not found")
            
            event_name, event_date = event
            
            # Get all sessions for this event
            cursor.execute("""
                SELECT 
                    s.id as session_id,
                    s.client_name,
                    f.name as frame_name,
                    s.amount_paid,
                    s.payment_status,
                    s.output_file_path,
                    s.captured_at,
                    s.printed_at,
                    s.usb_exported_at,
                    COUNT(DISTINCT p.id) as photo_count
                FROM sessions s
                JOIN frames f ON s.frame_id = f.id
                LEFT JOIN photos p ON s.id = p.session_id
                WHERE s.event_id = ?
                GROUP BY s.id
                ORDER BY s.captured_at ASC
            """, (event_id,))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                logger.warning(f"No sessions found for event {event_id}")
                return ""
            
            # Determine output path
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = Path("events") / f"{event_name}_{event_date}"
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"sessions_{event_name.replace(' ', '_')}_{timestamp}.csv"
            csv_path = output_path / csv_filename
            
            # Write CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Session ID',
                    'Client Name',
                    'Frame Name',
                    'Amount Paid (PHP)',
                    'Payment Status',
                    'Photo Count',
                    'Output File',
                    'Captured At',
                    'Printed At',
                    'USB Exported At'
                ])
                
                # Write session rows
                for session in sessions:
                    writer.writerow([
                        session['session_id'] if isinstance(session, dict) else session[0],
                        session['client_name'] or 'Anonymous' if isinstance(session, dict) else session[1] or 'Anonymous',
                        session['frame_name'] if isinstance(session, dict) else session[2],
                        f"{session['amount_paid']:.2f}" if isinstance(session, dict) else f"{session[3]:.2f}",
                        session['payment_status'] if isinstance(session, dict) else session[4],
                        session['photo_count'] if isinstance(session, dict) else session[5],
                        session['output_file_path'] or '' if isinstance(session, dict) else session[6] or '',
                        session['captured_at'] if isinstance(session, dict) else session[7],
                        session['printed_at'] or '' if isinstance(session, dict) else session[8] or '',
                        session['usb_exported_at'] or '' if isinstance(session, dict) else session[9] or ''
                    ])
            
            logger.info(f"Exported {len(sessions)} sessions to CSV: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise
    
    def export_all_events(self, output_dir: Optional[str] = None) -> str:
        """
        Export all events and sessions to a single CSV.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to exported CSV file
        """
        try:
            cursor = self.db.cursor()
            
            # Get all events
            cursor.execute("SELECT id, name, date, venue FROM events ORDER BY date DESC")
            events = cursor.fetchall()
            
            if not events:
                logger.warning("No events found to export")
                return ""
            
            # Determine output path
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = Path("exports")
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = output_path / f"all_events_{timestamp}.csv"
            
            # Write CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Event Name',
                    'Event Date',
                    'Venue',
                    'Session ID',
                    'Client Name',
                    'Frame Name',
                    'Amount Paid (PHP)',
                    'Payment Status',
                    'Captured At'
                ])
                
                # Write data for each event
                total_sessions = 0
                total_revenue = 0.0
                
                for event in events:
                    event_id, event_name, event_date, venue = event
                    
                    # Get sessions for this event
                    cursor.execute("""
                        SELECT 
                            s.id, s.client_name, f.name, 
                            s.amount_paid, s.payment_status, s.captured_at
                        FROM sessions s
                        JOIN frames f ON s.frame_id = f.id
                        WHERE s.event_id = ?
                        ORDER BY s.captured_at ASC
                    """, (event_id,))
                    
                    sessions = cursor.fetchall()
                    
                    for session in sessions:
                        writer.writerow([
                            event_name,
                            event_date,
                            venue or '',
                            session[0],
                            session[1] or 'Anonymous',
                            session[2],
                            f"{session[3]:.2f}",
                            session[4],
                            session[5]
                        ])
                        
                        total_sessions += 1
                        total_revenue += session[3]
                
                # Write summary row
                writer.writerow([])
                writer.writerow(['Summary', '', '', '', '', '', '', '', ''])
                writer.writerow(['Total Events', len(events), '', '', '', '', '', '', ''])
                writer.writerow(['Total Sessions', total_sessions, '', '', '', '', '', '', ''])
                writer.writerow(['Total Revenue', f"PHP {total_revenue:.2f}", '', '', '', '', '', '', ''])
            
            logger.info(f"Exported {len(events)} events ({total_sessions} sessions) to CSV: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise
    
    def generate_daily_report(self, date: Optional[str] = None) -> dict:
        """
        Generate daily summary statistics.
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            Dict with daily stats
        """
        try:
            cursor = self.db.cursor()
            
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Get daily stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    COALESCE(SUM(amount_paid), 0) as total_revenue,
                    COALESCE(AVG(amount_paid), 0) as avg_payment,
                    COALESCE(MIN(amount_paid), 0) as min_payment,
                    COALESCE(MAX(amount_paid), 0) as max_payment,
                    COUNT(CASE WHEN payment_status = 'Paid' THEN 1 END) as paid_count,
                    COUNT(CASE WHEN payment_status = 'Unpaid' THEN 1 END) as unpaid_count,
                    COUNT(CASE WHEN payment_status = 'Complimentary' THEN 1 END) as comp_count,
                    COUNT(CASE WHEN printed_at IS NOT NULL THEN 1 END) as printed_count,
                    COUNT(CASE WHEN usb_exported_at IS NOT NULL THEN 1 END) as usb_count
                FROM sessions
                WHERE DATE(captured_at) = ?
            """, (date,))
            
            stats = cursor.fetchone()
            
            # Get most popular frame
            cursor.execute("""
                SELECT f.name, COUNT(s.id) as usage_count
                FROM frames f
                JOIN sessions s ON f.id = s.frame_id
                WHERE DATE(s.captured_at) = ?
                GROUP BY f.id
                ORDER BY usage_count DESC
                LIMIT 1
            """, (date,))
            
            popular_frame = cursor.fetchone()
            
            # Get hourly distribution
            cursor.execute("""
                SELECT 
                    STRFTIME('%H', captured_at) as hour,
                    COUNT(*) as session_count
                FROM sessions
                WHERE DATE(captured_at) = ?
                GROUP BY hour
                ORDER BY hour ASC
            """, (date,))
            
            hourly_data = cursor.fetchall()
            
            report = {
                'date': date,
                'total_sessions': stats[0],
                'total_revenue': stats[1],
                'avg_payment': stats[2],
                'min_payment': stats[3],
                'max_payment': stats[4],
                'paid_count': stats[5],
                'unpaid_count': stats[6],
                'comp_count': stats[7],
                'printed_count': stats[8],
                'usb_count': stats[9],
                'popular_frame': popular_frame[0] if popular_frame else 'N/A',
                'popular_frame_count': popular_frame[1] if popular_frame else 0,
                'hourly_distribution': dict(hourly_data)
            }
            
            logger.info(f"Daily report for {date}: {stats[0]} sessions, PHP {stats[1]:.2f} revenue")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            return {}
    
    def export_daily_report_to_csv(self, date: Optional[str] = None,
                                  output_dir: Optional[str] = None) -> str:
        """
        Export daily report to CSV.
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            output_dir: Output directory
            
        Returns:
            Path to exported CSV file
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            report = self.generate_daily_report(date)
            
            if not report:
                return ""
            
            # Determine output path
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = Path("exports")
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            csv_path = output_path / f"daily_report_{date}.csv"
            
            # Write CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write report header
                writer.writerow(['Daily Session Report', date])
                writer.writerow([])
                
                # Write summary stats
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Sessions', report['total_sessions']])
                writer.writerow(['Total Revenue (PHP)', f"{report['total_revenue']:.2f}"])
                writer.writerow(['Average Payment (PHP)', f"{report['avg_payment']:.2f}"])
                writer.writerow(['Min Payment (PHP)', f"{report['min_payment']:.2f}"])
                writer.writerow(['Max Payment (PHP)', f"{report['max_payment']:.2f}"])
                writer.writerow([])
                
                # Payment breakdown
                writer.writerow(['Payment Status', 'Count'])
                writer.writerow(['Paid', report['paid_count']])
                writer.writerow(['Unpaid', report['unpaid_count']])
                writer.writerow(['Complimentary', report['comp_count']])
                writer.writerow([])
                
                # Activity stats
                writer.writerow(['Activity', 'Count'])
                writer.writerow(['Photos Printed', report['printed_count']])
                writer.writerow(['USB Exports', report['usb_count']])
                writer.writerow([])
                
                # Popular frame
                writer.writerow(['Most Popular Frame', report['popular_frame']])
                writer.writerow(['Frame Usage Count', report['popular_frame_count']])
                writer.writerow([])
                
                # Hourly distribution
                writer.writerow(['Hour', 'Sessions'])
                for hour, count in sorted(report['hourly_distribution'].items()):
                    writer.writerow([f"{hour}:00", count])
            
            logger.info(f"Daily report exported to CSV: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"Failed to export daily report: {e}")
            raise
