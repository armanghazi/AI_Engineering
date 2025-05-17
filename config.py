"""
Configuration settings for the Federal Register Chat application.
Modify these values according to your environment.
"""

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': '1234',
    'db': 'rag_chat',
    'charset': 'utf8mb4'
}

# Ollama configuration
OLLAMA_CONFIG = {
    'base_url': 'http://localhost:11434',
    'model_name': 'qwen2.5-0.5b'
}

# API configuration
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000
} 