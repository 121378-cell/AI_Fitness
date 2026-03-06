"""
Knowledge Base Module
Manages local SQLite database for storing and retrieving PDF knowledge.
"""

import sqlite3
import os
import json
from datetime import datetime


class KnowledgeBase:
    """
    Local SQLite-based knowledge base for storing PDF content chunks and metadata.
    """
    
    def __init__(self, db_path="data/knowledge_base/knowledge.db"):
        """Initialize knowledge base connection."""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    category TEXT,
                    source_path TEXT,
                    extracted_file TEXT,
                    chunk_count INTEGER,
                    keywords TEXT,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER NOT NULL,
                    chunk_num INTEGER,
                    text_content TEXT NOT NULL,
                    keywords TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)
            
            # Query cache table (for faster retrieval)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE,
                    results TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            print(f"✓ Knowledge base initialized at {self.db_path}")
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")
    
    def add_document(self, filename, category, source_path, extracted_file, chunks, keywords):
        """
        Add a document to the knowledge base.
        
        Args:
            filename (str): Document filename
            category (str): Document category (e.g., 'Training', 'Nutrition')
            source_path (str): Original PDF path
            extracted_file (str): Path to extracted text file
            chunks (list): List of text chunks
            keywords (list): List of keywords
            
        Returns:
            int: Document ID, or -1 if failed
        """
        try:
            cursor = self.conn.cursor()
            keywords_str = json.dumps(keywords)
            
            cursor.execute("""
                INSERT INTO documents (filename, category, source_path, extracted_file, chunk_count, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (filename, category, source_path, extracted_file, len(chunks), keywords_str))
            
            doc_id = cursor.lastrowid
            
            # Add chunks
            for chunk_num, chunk in enumerate(chunks):
                chunk_keywords = self._extract_chunk_keywords(chunk, keywords)
                cursor.execute("""
                    INSERT INTO chunks (doc_id, chunk_num, text_content, keywords)
                    VALUES (?, ?, ?, ?)
                """, (doc_id, chunk_num, chunk, json.dumps(chunk_keywords)))
            
            self.conn.commit()
            print(f"✓ Added document '{filename}' with {len(chunks)} chunks")
            return doc_id
        except sqlite3.IntegrityError:
            print(f"[!] Document '{filename}' already exists in knowledge base")
            return -1
        except Exception as e:
            print(f"Error adding document: {e}")
            return -1
    
    def search_knowledge(self, query, limit=5):
        """
        Search knowledge base for relevant chunks.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of relevant chunks with metadata
        """
        try:
            cursor = self.conn.cursor()
            
            # Build search query
            keywords = query.lower().split()
            where_conditions = []
            params = []
            
            for keyword in keywords:
                if len(keyword) > 3:  # Only search meaningful words
                    where_conditions.append("LOWER(text_content) LIKE ?")
                    params.append(f"%{keyword}%")
            
            if not where_conditions:
                return []
            
            sql = f"""
                SELECT 
                    c.id as chunk_id, 
                    c.chunk_num,
                    c.text_content,
                    d.filename,
                    d.category
                FROM chunks c
                JOIN documents d ON c.doc_id = d.id
                WHERE {' OR '.join(where_conditions)}
                LIMIT ?
            """
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def get_all_documents(self):
        """
        Get list of all documents in knowledge base.
        
        Returns:
            list: List of document dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, filename, category, chunk_count, date_added FROM documents
                ORDER BY date_added DESC
            """)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
    
    def delete_document(self, doc_id):
        """
        Delete a document from the knowledge base.
        
        Args:
            doc_id (int): Document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            self.conn.commit()
            print(f"✓ Deleted document {doc_id}")
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def _extract_chunk_keywords(self, chunk, doc_keywords):
        """
        Extract keywords relevant to a specific chunk.
        
        Args:
            chunk (str): Chunk text
            doc_keywords (list): Document-level keywords
            
        Returns:
            list: Relevant keywords for this chunk
        """
        chunk_lower = chunk.lower()
        return [kw for kw in doc_keywords if kw.lower() in chunk_lower]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Example usage
    kb = KnowledgeBase()
    docs = kb.get_all_documents()
    print(f"Documents in knowledge base: {len(docs)}")
    for doc in docs:
        print(f"  - {doc['filename']} ({doc['chunk_count']} chunks)")
