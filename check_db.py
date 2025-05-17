import sqlite3
from pathlib import Path

def check_database():
    db_path = Path("data_pipeline/rag_chat.db")
    if not db_path.exists():
        print("Database file not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check documents count
    cursor.execute("SELECT COUNT(*) FROM federal_register_documents")
    count = cursor.fetchone()[0]
    print(f"Number of documents in database: {count}")

    # Check pipeline logs
    cursor.execute("SELECT * FROM pipeline_logs ORDER BY created_at DESC LIMIT 5")
    logs = cursor.fetchall()
    print("\nRecent pipeline logs:")
    for log in logs:
        print(f"Pipeline: {log[1]}, Status: {log[2]}, Records: {log[5]}")

    conn.close()

if __name__ == "__main__":
    check_database() 