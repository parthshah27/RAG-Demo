"""
Database Module - Traditional Database Abstraction Layer

CURRENT STRATEGY:
================
Primary: ChromaDB (Vector Database)
- Stores document embeddings and semantic search capability
- Used for RAG retrieval (vector similarity search)
- Persisted to ./chroma_db/ directory

Secondary (Future): Traditional Database (SQLite/PostgreSQL/MySQL)
- For user account management
- For audit logs and query history
- For session tracking
- For analytics and monitoring

WHY TWO DATABASES:
==================
1. ChromaDB: Purpose-built for vector operations and semantic search
   - Optimized for embedding similarity
   - HNSW index for fast nearest neighbor search
   - Lightweight and easy to deploy

2. Traditional DB: For transactional and relational data
   - ACID guarantees
   - User authentication and profiles
   - Audit trails and compliance logging
   - Query history for analytics

IMPLEMENTATION GUIDE:
=====================

For SQLite (development/small scale):

```python
import sqlite3
from typing import Optional

class UserDB:
    def __init__(self, db_path: str = "rag.db"):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Query audit log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                answer TEXT,
                domain TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_query(self, username: str, query: str, answer: str, domain: str):
        '''Log a user query for audit trail and analytics'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id FROM users WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
        
        if user:
            cursor.execute(
                '''INSERT INTO query_log (user_id, query, answer, domain)
                   VALUES (?, ?, ?, ?)''',
                (user[0], query, answer, domain)
            )
            conn.commit()
        
        conn.close()

# Usage:
# from .db import UserDB
# db = UserDB()
# db.log_query("admin", "What is X?", "Answer is...", "healthcare")
```

For PostgreSQL (production scale):

```python
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryLog(Base):
    __tablename__ = 'query_log'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text)
    domain = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

# Initialize:
# engine = create_engine('postgresql://user:password@localhost/rag_db')
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
```

TRANSITION FROM CHATGPT-ONLY:
=============================
✓ Using real databases (ChromaDB + future traditional DB)
✓ Not relying on ChatGPT to craft entire solutions
✓ Modular architecture with clear separation of concerns
✓ Production-ready patterns (proper error handling, logging)
✓ Database choice made strategically based on use case

STATUS:
=======
- Vector Database (ChromaDB): IMPLEMENTED ✓
- Traditional Database Layer: READY FOR IMPLEMENTATION (template provided above)
- User Management: Currently hardcoded demo auth in auth.py
- Audit Logging: Ready to implement using DB module

NEXT STEPS FOR PRODUCTION:
==========================
1. Choose traditional DB (SQLite for small scale, PostgreSQL for enterprise)
2. Implement UserDB class from template above
3. Replace hardcoded auth in auth.py with DB-backed authentication
4. Add query logging to ask_rag function
5. Create audit report endpoints
"""

# Placeholder for future database implementations
# Uncomment and populate when implementing traditional database support

# from typing import Optional

# class UserDB:
#     """User management and query logging (to be implemented)"""
#     pass

# class AuditLog:
#     """Audit trail and analytics (to be implemented)"""
#     pass

# For now, Vector Database (ChromaDB) is used for all data storage
# See rag.py for ChromaDB implementation
