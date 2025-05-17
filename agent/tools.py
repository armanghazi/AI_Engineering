import aiomysql
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .db_config import DB_CONFIG

async def search_documents_by_date(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Search for documents within a date range."""
    pool = await aiomysql.create_pool(**DB_CONFIG)
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                sql = """
                SELECT id, document_number, title, abstract, document_type, 
                       publication_date, agency_names
                FROM federal_register_documents
                WHERE publication_date BETWEEN %s AND %s
                ORDER BY publication_date DESC
                """
                await cur.execute(sql, (start_date, end_date))
                results = await cur.fetchall()
                return [dict(row) for row in results]
    finally:
        pool.close()
        await pool.wait_closed()

async def search_documents_by_agency(agency_name: str) -> List[Dict[str, Any]]:
    """Search for documents from a specific agency."""
    pool = await aiomysql.create_pool(**DB_CONFIG)
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                sql = """
                SELECT id, document_number, title, abstract, document_type, 
                       publication_date, agency_names
                FROM federal_register_documents
                WHERE agency_names LIKE %s
                ORDER BY publication_date DESC
                """
                await cur.execute(sql, (f'%{agency_name}%',))
                results = await cur.fetchall()
                return [dict(row) for row in results]
    finally:
        pool.close()
        await pool.wait_closed()

async def get_latest_documents(limit: int = 10) -> List[Dict[str, Any]]:
    """Get the most recent documents."""
    pool = await aiomysql.create_pool(**DB_CONFIG)
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                sql = """
                SELECT id, document_number, title, abstract, document_type, 
                       publication_date, agency_names
                FROM federal_register_documents
                ORDER BY publication_date DESC
                LIMIT %s
                """
                await cur.execute(sql, (limit,))
                results = await cur.fetchall()
                return [dict(row) for row in results]
    finally:
        pool.close()
        await pool.wait_closed()

async def search_documents_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    """Search for documents containing specific keywords in title or abstract."""
    pool = await aiomysql.create_pool(**DB_CONFIG)
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                sql = """
                SELECT id, document_number, title, abstract, document_type, 
                       publication_date, agency_names
                FROM federal_register_documents
                WHERE title LIKE %s OR abstract LIKE %s
                ORDER BY publication_date DESC
                """
                search_term = f'%{keyword}%'
                await cur.execute(sql, (search_term, search_term))
                results = await cur.fetchall()
                return [dict(row) for row in results]
    finally:
        pool.close()
        await pool.wait_closed()

# Tool definitions for the agent
TOOLS = [
    {
        "name": "search_documents_by_date",
        "description": "Search for Federal Register documents within a date range",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format"
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "search_documents_by_agency",
        "description": "Search for Federal Register documents from a specific agency",
        "parameters": {
            "type": "object",
            "properties": {
                "agency_name": {
                    "type": "string",
                    "description": "Name of the agency to search for"
                }
            },
            "required": ["agency_name"]
        }
    },
    {
        "name": "get_latest_documents",
        "description": "Get the most recent Federal Register documents",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of documents to return",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "search_documents_by_keyword",
        "description": "Search for Federal Register documents containing specific keywords",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search for in title or abstract"
                }
            },
            "required": ["keyword"]
        }
    }
] 