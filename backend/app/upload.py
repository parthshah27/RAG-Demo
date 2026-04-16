"""
File Upload and Indexing Module

Handles file uploads (CSV, TXT) and dynamically indexes content into ChromaDB.
Allows users to augment the knowledge base at runtime with their own files.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from .rag import get_collection, get_embedding
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/")
async def index_uploaded_file(upload: UploadFile = File(...)):
    """
    Upload and index user files into the RAG knowledge base.
    
    Supported formats:
    - CSV: Each row becomes a searchable document
    - TXT/MD: Entire file content indexed
    
    Process:
    1. Read file content
    2. Parse and convert to documents
    3. Generate embeddings for each document
    4. Add to ChromaDB collection
    
    Args:
        upload (UploadFile): File to upload and index
        
    Returns:
        JSONResponse: Status, number of indexed documents, sample IDs
        
    Raises:
        HTTPException: 400 if file is empty or invalid format
        HTTPException: 500 if processing fails
    """
    if not upload.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        content = await upload.read()
        content_str = content.decode('utf-8')
        
        docs = []
        ids = []
        
        # CSV: Process rows
        if upload.filename.lower().endswith('.csv'):
            import pandas as pd
            from io import StringIO
            df = pd.read_csv(StringIO(content_str))
            df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]
            
            # Convert each row to a document
            for idx, row in df.iterrows():
                text_parts = [f"{col}:{val}" for col, val in row.items() if pd.notna(val) and str(val).strip()]
                if text_parts:
                    text = " | ".join(text_parts)
                    docs.append(text)
                    ids.append(f"{upload.filename.replace(' ', '_').replace('/', '_')}_{idx}")
        else:
            # TXT/MD: Use entire content as single document
            docs = [content_str[:10000]]  # Truncate long files
            ids = [upload.filename.replace(" ", "_").replace("/", "_")]
        
        if not docs:
            raise HTTPException(status_code=400, detail="No valid content extracted from file")
        
        # Generate embeddings and add to vector database
        embeddings = [get_embedding(doc) for doc in docs]
        get_collection().add(
            documents=docs, 
            embeddings=embeddings, 
            ids=ids
        )
        
        return JSONResponse(content={
            "status": "success",
            "indexed": len(docs),
            "sample_ids": ids[:5],
            "filename": upload.filename
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
