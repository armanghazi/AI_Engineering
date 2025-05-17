# RAG Chat System with Daily Data Updates

This project implements a RAG (Retrieval-Augmented Generation) based chat system that uses daily updated data from the Federal Register API. The system consists of four main components:

1. Data Pipeline
2. Agent System
3. API Interface
4. Basic UI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MySQL database:
```sql
CREATE DATABASE rag_chat;
```

3. Create a `.env` file with the following variables:
```
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=rag_chat
OLLAMA_BASE_URL=http://localhost:11434
```

4. Run the data pipeline:
```bash
python data_pipeline/main.py
```

5. Start the API server:
```bash
uvicorn api.main:app --reload
```

## Project Structure

```
.
├── data_pipeline/         # Data pipeline components
├── agent/                # Agent system implementation
├── api/                  # FastAPI application
├── static/              # Static files for UI
├── templates/           # HTML templates
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Features

- Daily data updates from Federal Register API
- Asynchronous processing
- Tool-based agent system
- Simple web interface for chat
- MySQL database for data storage

## Usage

1. Access the web interface at `http://localhost:8000`
2. Enter your query in the chat interface
3. The agent will process your query and provide a response based on the latest data

## Note

This is a demo project and may not include all production-grade features like authentication, logging, or vector database integration. 