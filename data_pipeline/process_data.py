import json
import asyncio
import aiofiles
from datetime import datetime
from pathlib import Path
import aiosqlite
import logging
from typing import List, Dict, Any
from data_pipeline.utils import get_db_path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederalRegisterProcessor:
    def __init__(self, raw_data_dir="data_pipeline/raw_data"):
        self.raw_data_dir = Path(raw_data_dir)
        
    async def process_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Process a single JSON file of Federal Register documents."""
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                documents = json.loads(content)
            
            if not isinstance(documents, list):
                logger.error(f"Expected a list of documents, got {type(documents)}")
                return []
            
            processed_docs = []
            for doc in documents:
                try:
                    # Use document_number as the unique id
                    doc_id = str(doc.get('document_number', ''))
                    processed_doc = {
                        'id': doc_id,
                        'document_number': doc_id,
                        'title': str(doc.get('title', '')).strip(),
                        'abstract': str(doc.get('abstract', '')).strip(),
                        'document_type': str(doc.get('type', '')),
                        'publication_date': str(doc.get('publication_date', '')),
                        'agency_names': ', '.join(str(agency) for agency in doc.get('agencies', [])),
                        'raw_json': json.dumps(doc)
                    }
                    
                    # Only add documents with required fields
                    if all([
                        processed_doc['id'],
                        processed_doc['title'],
                        processed_doc['publication_date']
                    ]):
                        processed_docs.append(processed_doc)
                except Exception as e:
                    logger.error(f"Error processing document: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_docs)} documents")
            return processed_docs
            
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {str(e)}")
            return []
    
    async def save_to_database(self, documents: List[Dict[str, Any]], db_path: Path) -> int:
        """Save processed documents to SQLite database."""
        if not documents:
            logger.warning("No documents to save")
            return 0
            
        try:
            async with aiosqlite.connect(db_path) as db:
                # Insert documents
                for doc in documents:
                    sql = """
                    INSERT INTO federal_register_documents 
                    (id, document_number, title, abstract, document_type, 
                     publication_date, agency_names, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    abstract = excluded.abstract,
                    document_type = excluded.document_type,
                    publication_date = excluded.publication_date,
                    agency_names = excluded.agency_names,
                    raw_json = excluded.raw_json
                    """
                    await db.execute(sql, (
                        doc['id'],
                        doc['document_number'],
                        doc['title'],
                        doc['abstract'],
                        doc['document_type'],
                        doc['publication_date'],
                        doc['agency_names'],
                        doc['raw_json']
                    ))
                
                await db.commit()
            logger.info(f"Successfully saved {len(documents)} documents to database")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            return 0
    
    async def process_latest_data(self, db_path: Path) -> int:
        """Process the most recent data file."""
        try:
            # Get the most recent file
            files = list(self.raw_data_dir.glob('federal_register_*.json'))
            if not files:
                logger.warning("No data files found to process")
                return 0
            
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Processing file: {latest_file}")
            
            # Process and save to database
            processed_docs = await self.process_file(latest_file)
            if processed_docs:
                saved_count = await self.save_to_database(processed_docs, db_path)
                return saved_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error in process_latest_data: {str(e)}")
            return 0

async def main():
    """Main function to run the processor."""
    db_path = get_db_path()
    processor = FederalRegisterProcessor()
    count = await processor.process_latest_data(db_path)
    logger.info(f"Pipeline completed. Processed {count} documents.")

if __name__ == "__main__":
    asyncio.run(main()) 