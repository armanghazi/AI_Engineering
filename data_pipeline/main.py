import asyncio
import aiomysql
from datetime import datetime
from .downloader import FederalRegisterDownloader
from .processor import FederalRegisterProcessor
from .db_config import DB_CONFIG

async def log_pipeline_run(pool, status, records_processed, error_message=None):
    """Log pipeline execution details to database."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = """
            INSERT INTO pipeline_logs 
            (pipeline_name, status, start_time, end_time, records_processed, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            await cur.execute(sql, (
                'federal_register_pipeline',
                status,
                datetime.now(),
                datetime.now(),
                records_processed,
                error_message
            ))
            await conn.commit()

async def run_pipeline():
    """Run the complete data pipeline."""
    # Create database connection pool
    pool = await aiomysql.create_pool(**DB_CONFIG)
    
    try:
        # Download new data
        downloader = FederalRegisterDownloader()
        records_downloaded = await downloader.download_daily_data()
        
        if records_downloaded > 0:
            # Process and save to database
            processor = FederalRegisterProcessor()
            records_processed = await processor.process_latest_data()
            
            # Log successful run
            await log_pipeline_run(pool, 'success', records_processed)
            print(f"Pipeline completed successfully. Processed {records_processed} records.")
        else:
            await log_pipeline_run(pool, 'no_new_data', 0)
            print("No new data to process.")
            
    except Exception as e:
        error_message = str(e)
        await log_pipeline_run(pool, 'error', 0, error_message)
        print(f"Pipeline failed: {error_message}")
        
    finally:
        pool.close()
        await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(run_pipeline()) 