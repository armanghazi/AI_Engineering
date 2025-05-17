import logging
import aiosqlite
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("data_pipeline/rag_chat.db")

async def log_pipeline_run(db_path: Path, status: str, records_processed: int, error_message: str = None) -> None:
    """Log pipeline execution details to database."""
    try:
        async with aiosqlite.connect(db_path) as db:
            sql = """
            INSERT INTO pipeline_logs 
            (pipeline_name, status, start_time, end_time, records_processed, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            await db.execute(sql, (
                'federal_register_pipeline',
                status,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                records_processed,
                error_message
            ))
            await db.commit()
    except Exception as e:
        logger.error(f"Error logging pipeline run: {str(e)}")

def get_db_path() -> Path:
    """Get database path."""
    return DB_PATH

async def create_database_if_not_exists() -> None:
    """Create the database and tables if they don't exist."""
    try:
        # Ensure the directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(DB_PATH) as db:
            # Create tables
            await db.execute("""
            CREATE TABLE IF NOT EXISTS federal_register_documents (
                id TEXT PRIMARY KEY,
                document_number TEXT,
                title TEXT,
                abstract TEXT,
                document_type TEXT,
                publication_date TEXT,
                agency_names TEXT,
                raw_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            await db.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                records_processed INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            await db.commit()
        
        logger.info("Database and tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise 