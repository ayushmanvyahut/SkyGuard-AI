
import sqlite3

conn = sqlite3.connect("skyguard_alerts.db")
cursor = conn.cursor()

cursor.execute("""
SELECT id, event, event_time, status
FROM alerts
ORDER BY id DESC
""")

rows = cursor.fetchall()

print("\n--- SKYGUARD AI ALERT HISTORY ---")

for row in rows:
    print(f"ID: {row[0]}")
    print(f"Event: {row[1]}")
    print(f"Time: {row[2]}")
    print(f"Status: {row[3]}")
    print("-" * 30)

conn.close()