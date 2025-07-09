import sqlite3
import os
import time
import psutil
import getpass
from datetime import datetime

DB_NAME = 'monitoring.db'
PROCESS_THRESHOLD = 800     # Absolute threshold for process count
TIME_WINDOW = 2             # Time window in seconds for rate calculation
RATE_THRESHOLD = 25         # Process growth rate threshold (processes/second)

def get_db_connection():
    """
    Create and return a connection to the SQLite database with WAL journal mode for improved concurrency.
    """
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

def get_recent_process_counts(window_seconds=2):
    """
    Retrieve process count data from the database within the specified time window.
    
    Args:
        window_seconds: Number of seconds to look back in history
        
    Returns:
        List of tuples containing (timestamp, process_count)
    """
    retries = 3
    while retries > 0:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT timestamp, process_count FROM process_monitor
                WHERE timestamp >= datetime('now', '-{window_seconds} seconds')
                ORDER BY timestamp ASC
            """)
            results = cursor.fetchall()
            conn.close()
            return [(row["timestamp"], row["process_count"]) for row in results]
        except sqlite3.OperationalError:
            retries -= 1
            time.sleep(0.5)
    return []
    

def detect_fork_bomb():
    """
    Checks for potential fork bomb attacks using two detection methods:
    1. Absolute threshold: Is the current process count above PROCESS_THRESHOLD?
    2. Growth rate: Is the process count increasing faster than RATE_THRESHOLD?
    
    Returns:
        Tuple of (is_attack_detected, current_process_count, growth_rate)
    """
    process_count = len(psutil.pids())
    
    # Method 1: Check absolute process count
    if process_count > PROCESS_THRESHOLD:
        return True, process_count, 0

    # Method 2: Check process growth rate
    counts = get_recent_process_counts(TIME_WINDOW)
    if len(counts) >= 2:
        rate = (counts[-1][1] - counts[0][1]) / TIME_WINDOW
        if rate > RATE_THRESHOLD:
            return True, process_count, rate

    return False, process_count, 0

def mitigate_fork_bomb():
    """
    Execute mitigation strategies when a fork bomb is detected:
    1. Log the detection event
    2. Kill all processes owned by the current user
    3. Record the mitigation action in the database
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ATTACK DETECTED! Initiating mitigation...")

    username = getpass.getuser()

    try:
        # Kill all processes owned by this user
        os.system(f"killall -KILL -u {username}")
    except Exception:
        pass

    # Log mitigation action to database
    now = datetime.now()
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("CREATE TABLE IF NOT EXISTS mitigation_log (timestamp TEXT, action TEXT)")
    cursor.execute("INSERT INTO mitigation_log VALUES (?, ?)", (timestamp, "fork bomb mitigation applied"))
    conn.commit()
    conn.close()

    print(f"[{timestamp}] Mitigation complete.")

def main():
    """
    Main loop that continuously checks for fork bomb attacks and triggers mitigation
    when necessary, with a cooldown period to prevent repeated mitigations.
    """
    last_mitigation_time = 0

    while True:
        # Check for fork bomb attack
        is_attack, count, rate = detect_fork_bomb()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_attack:
            print(f"[{now}] [ALERT] Fork bomb detected. Process count: {count}, Rate: {rate:.2f} proc/sec")
            current_time = time.time()
            
            # Apply mitigation with a 60-second cooldown
            if current_time - last_mitigation_time > 60:
                mitigate_fork_bomb()
                last_mitigation_time = current_time

        time.sleep(1)  # Check once per second

if __name__ == "__main__":
    main()