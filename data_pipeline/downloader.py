import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import os
from pathlib import Path

class FederalRegisterDownloader:
    BASE_URL = "https://www.federalregister.gov/api/v1/documents"
    
    def __init__(self, output_dir="data_pipeline/raw_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def fetch_documents(self, start_date, end_date):
        """Fetch documents from Federal Register API for a date range."""
        params = {
            "conditions[publication_date][gte]": start_date,
            "conditions[publication_date][lte]": end_date,
            "per_page": 1000,
            "order": "newest"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    raise Exception(f"Failed to fetch data: {response.status}")
    
    async def download_daily_data(self):
        """Download today's data and save to file."""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        try:
            documents = await self.fetch_documents(
                yesterday.isoformat(),
                today.isoformat()
            )
            
            if documents:
                # Save to file with date in filename
                filename = f"federal_register_{today.isoformat()}.json"
                filepath = self.output_dir / filename
                
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(json.dumps(documents, indent=2))
                
                return len(documents)
            return 0
            
        except Exception as e:
            print(f"Error downloading data: {str(e)}")
            return 0

if __name__ == "__main__":
    # Test the downloader
    downloader = FederalRegisterDownloader()
    asyncio.run(downloader.download_daily_data()) 