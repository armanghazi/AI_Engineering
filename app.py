from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import aiosqlite
from pathlib import Path
import logging
from typing import List, Dict

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

async def search_documents(query: str) -> List[Dict]:
    """Search for relevant documents in the database."""
    db_path = Path("data_pipeline/rag_chat.db")
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return []

    try:
        async with aiosqlite.connect(db_path) as db:
            search_query = """
                SELECT id, document_number, title, abstract, publication_date, agency_names 
                FROM federal_register_documents 
                WHERE title LIKE ? OR abstract LIKE ?
                ORDER BY publication_date DESC 
                LIMIT 5
            """
            search_term = f"%{query}%"
            async with db.execute(search_query, (search_term, search_term)) as cursor:
                rows = await cursor.fetchall()
            
            return [{
                "id": row[0],
                "document_number": row[1],
                "title": row[2],
                "abstract": row[3],
                "publication_date": row[4],
                "agency_names": row[5]
            } for row in rows]
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return []

async def generate_response(query: str, context_docs: List[Dict]) -> str:
    """Generate a response using the context documents."""
    if not context_docs:
        return "I couldn't find any relevant documents to answer your question. Could you please rephrase or try a different question?"
    
    context = "\n\n".join([
        f"Document {doc['document_number']} ({doc['publication_date']}):\n"
        f"Title: {doc['title']}\n"
        f"Abstract: {doc['abstract']}\n"
        f"Agency: {doc['agency_names']}"
        for doc in context_docs
    ])
    
    return f"Based on the Federal Register documents, here's what I found:\n\n{context}"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the chat interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": []
    })

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, query: str = Form(...)):
    """Handle chat messages and return responses."""
    try:
        context_docs = await search_documents(query)
        response = await generate_response(query, context_docs)
        return templates.TemplateResponse("chat_messages.html", {
            "request": request,
            "messages": [
                ChatMessage("user", query),
                ChatMessage("assistant", response)
            ]
        })
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Error processing your request: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="debug") 