import aiohttp
import asyncio
import aiofiles
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederalRegisterFetcher:
    def __init__(self, output_dir="data_pipeline/raw_data"):
        self.base_url = "https://www.federalregister.gov/api/v1/documents"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def fetch_documents(self, start_date: str, end_date: str) -> list:
        """Fetch documents from the Federal Register API for a date range."""
        params = {
            'conditions[publication_date][gte]': start_date,
            'conditions[publication_date][lte]': end_date,
            'per_page': 1000,
            'order': 'newest'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"API request failed with status {response.status}")
                        return []
                    
                    data = await response.json()
                    if not isinstance(data, dict) or 'results' not in data:
                        logger.error("Invalid API response format")
                        return []
                    
                    documents = data['results']
                    logger.info(f"Found {len(documents)} documents")
                    return documents
                    
        except Exception as e:
            logger.error(f"Error fetching documents: {str(e)}")
            return []
    
    async def fetch_2024_2025_data(self) -> int:
        """Fetch documents from 2024-01-01 to 2025-12-31."""
        start_str = '2024-01-01'
        end_str = '2025-12-31'
        
        logger.info(f"Fetching documents from {start_str} to {end_str}")
        
        documents = await self.fetch_documents(start_str, end_str)
        if not documents:
            logger.warning("No documents found")
            return 0
        
        # Save to file
        output_file = self.output_dir / "federal_register_2024_2025.json"
        try:
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(documents, indent=2))
            logger.info(f"Saved {len(documents)} documents to {output_file}")
            return len(documents)
        except Exception as e:
            logger.error(f"Error saving documents: {str(e)}")
            return 0

async def main():
    """Main function to run the fetcher."""
    fetcher = FederalRegisterFetcher()
    count = await fetcher.fetch_2024_2025_data()
    logger.info(f"Pipeline completed. Fetched {count} documents.")

if __name__ == "__main__":
    asyncio.run(main()) 