import psutil
import sqlite3
import time
from datetime import datetime

DB_NAME = 'monitoring.db'

def get_db_connection():
    """
    Create and return a connection to the SQLite database with WAL journal mode.
    WAL (Write-Ahead Logging) improves concurrent access between the monitoring
    and detector processes.
    """
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL;')  # Enable Write-Ahead Logging
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize the database by creating the process_monitor table if it doesn't exist.
    This table will store timestamp and process count data.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS process_monitor (
                timestamp TEXT,
                process_count INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error initializing the database: {e}")

def log_process_count():
    """
    Count all processes currently running on the system and log the count
    to the database along with the current timestamp.
    """
    # Get current process count using psutil
    count = len(psutil.pids())
    now = datetime.now().isoformat()  # ISO format with microseconds

    # Insert record into database
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO process_monitor (timestamp, process_count) VALUES (?, ?)", (now, count))
    conn.commit()
    conn.close()

    print(f"[{now}] Process Count: {count}")
   
    # For debugging/verification: retrieve the last record
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM process_monitor ORDER BY timestamp DESC LIMIT 1")
    last_row = c.fetchone()
    conn.close()

if __name__ == '__main__':
    """
    Main execution flow:
    1. Initialize the database
    2. Enter infinite loop to continuously monitor process counts
    """
    init_db()
    while True:
        log_process_count()
        time.sleep(1)  # Log process count every second