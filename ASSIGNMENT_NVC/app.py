import sqlite3
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)
DB_PATH = "veritas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get today's date prefix (YYYY-MM-DD)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # FR-5.1 Daily Ingestion Stats
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT record_id) as total_received,
            SUM(CASE WHEN (
                hemoglobin_analytics = 'Invalid' OR 
                wbc_analytics = 'Invalid' OR 
                platelets_analytics = 'Invalid'
            ) THEN 1 ELSE 0 END) as total_failed,
            SUM(CASE WHEN (
                hemoglobin_analytics IN ('Outlier', 'Above Range', 'Below Range') OR 
                wbc_analytics IN ('Outlier', 'Above Range', 'Below Range') OR 
                platelets_analytics IN ('Outlier', 'Above Range', 'Below Range')
            ) THEN 1 ELSE 0 END) as total_flagged
        FROM claims_analytics
        WHERE ingestion_timestamp LIKE ?;
    """, (f"{today}%",))

    stats = cursor.fetchone()
    conn.close()

    total_received = stats["total_received"] or 0
    total_failed = stats["total_failed"] or 0
    total_flagged = stats["total_flagged"] or 0
    total_processed = total_received - total_failed

    return render_template(
        "dashboard.html",
        date=today,
        received=total_received,
        processed=total_processed,
        failed=total_failed,
        flagged=total_flagged
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)