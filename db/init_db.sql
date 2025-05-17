-- Create the database
CREATE DATABASE IF NOT EXISTS rag_chat;
USE rag_chat;

-- Create the federal_register_documents table
CREATE TABLE IF NOT EXISTS federal_register_documents (
    id VARCHAR(255) PRIMARY KEY,
    document_number VARCHAR(50),
    title TEXT,
    abstract TEXT,
    document_type VARCHAR(100),
    publication_date DATE,
    agency_names TEXT,
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the pipeline_logs table
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pipeline_name VARCHAR(100),
    status VARCHAR(50),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    records_processed INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 