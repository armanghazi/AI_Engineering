import json
import asyncio
import aiofiles
from datetime import datetime
from pathlib import Path
import aiomysql
from .db_config import DB_CONFIG, CREATE_TABLES_SQL

class FederalRegisterProcessor:
    def __init__(self, raw_data_dir="data_pipeline/raw_data"):
        self.raw_data_dir = Path(raw_data_dir)
        
    async def process_file(self, filepath):
        """Process a single JSON file of Federal Register documents."""
        async with aiofiles.open(filepath, 'r') as f:
            content = await f.read()
            documents = json.loads(content)
        
        processed_docs = []
        for doc in documents:
            processed_doc = {
                'id': doc.get('id'),
                'document_number': doc.get('document_number'),
                'title': doc.get('title'),
                'abstract': doc.get('abstract'),
                'document_type': doc.get('type'),
                'publication_date': doc.get('publication_date'),
                'agency_names': ', '.join(doc.get('agencies', [])),
                'raw_json': json.dumps(doc)
            }
            processed_docs.append(processed_doc)
        
        return processed_docs
    
    async def save_to_database(self, documents):
        """Save processed documents to MySQL database."""
        pool = await aiomysql.create_pool(**DB_CONFIG)
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Create tables if they don't exist
                await cur.execute(CREATE_TABLES_SQL)
                
                # Insert documents
                for doc in documents:
                    sql = """
                    INSERT INTO federal_register_documents 
                    (id, document_number, title, abstract, document_type, 
                     publication_date, agency_names, raw_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    abstract = VALUES(abstract),
                    document_type = VALUES(document_type),
                    publication_date = VALUES(publication_date),
                    agency_names = VALUES(agency_names),
                    raw_json = VALUES(raw_json)
                    """
                    await cur.execute(sql, (
                        doc['id'],
                        doc['document_number'],
                        doc['title'],
                        doc['abstract'],
                        doc['document_type'],
                        doc['publication_date'],
                        doc['agency_names'],
                        doc['raw_json']
                    ))
                
                await conn.commit()
        
        pool.close()
        await pool.wait_closed()
    
    async def process_latest_data(self):
        """Process the most recent data file."""
        try:
            # Get the most recent file
            files = list(self.raw_data_dir.glob('federal_register_*.json'))
            if not files:
                return 0
            
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            
            # Process and save to database
            processed_docs = await self.process_file(latest_file)
            await self.save_to_database(processed_docs)
            
            return len(processed_docs)
            
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            return 0

if __name__ == "__main__":
    # Test the processor
    processor = FederalRegisterProcessor()
    asyncio.run(processor.process_latest_data()) 