from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from .auth import login_user, SECRET, ALGORITHM

from .rag import CONFIG, ask_rag_async, initialize_rag
from .upload import router as upload_router


"""
RAG Application - Main API Server

This FastAPI application provides endpoints for:
1. User authentication (JWT-based)
2. Configuration retrieval (domain-specific settings)
3. RAG queries with vector similarity search using ChromaDB
4. File uploads for document indexing

Architecture:
- Vector Database: ChromaDB for semantic search
- LLM Integration: OpenAI-compatible API (configurable provider)
- Authentication: JWT tokens with OAuth2
- Frontend Communication: REST API with CORS enabled

Database Strategy:
- PRIMARY: ChromaDB (vector store for document embeddings)
- FUTURE: Traditional database (SQLite/PostgreSQL) for:
  * User account management
  * Audit logs and query history
  * Session tracking
"""


# Pydantic models for request validation
class LoginRequest(BaseModel):
    """Login request with username and password credentials."""
    username: str
    password: str


class AskRequest(BaseModel):
    """Query request for RAG system."""
    query: str = Field(min_length=1, description="User question to query RAG knowledge base")



@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifecycle manager.
    
    Startup: Initialize RAG system (load data into ChromaDB)
    Shutdown: Cleanup resources
    """
    # Initialize RAG knowledge base at startup
    initialize_rag()
    yield
    # Cleanup happens here after shutdown



app = FastAPI(lifespan=lifespan)
app.include_router(upload_router)

# OAuth2 scheme for securing endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Verify JWT token and extract username.
    
    Args:
        token (str): JWT token from Authorization header
        
    Returns:
        str: Verified username
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")


# CORS middleware: Allow frontend to call backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/config")
async def get_config() -> JSONResponse:
    """
    Retrieve domain-specific configuration.
    
    Returns:
        JSONResponse: Configuration object containing:
        - domain: Current domain (e.g., 'healthcare', 'retail')
        - title: Application title
        - ui: UI configuration (placeholders, file types, sample queries)
        - dashboard: Metrics and insights for UI display
        - system_prompt: Domain-specific system prompt for LLM
    """
    return JSONResponse(content=CONFIG, media_type="application/json; charset=utf-8")


@app.post("/login")
async def login(data: LoginRequest) -> dict:
    """
    Authenticate user and return JWT token.
    
    Args:
        data (LoginRequest): Username and password
        
    Returns:
        dict: {"token": "<JWT_TOKEN>"}
        
    Raises:
        HTTPException: 401 if credentials are invalid
        
    Security:
        - Tokens expire based on JWT configuration
        - In production: Use password hashing and secure secrets management
    """
    result = login_user(data.username, data.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@app.post("/ask")
async def ask(data: AskRequest, token: str = Depends(verify_token)) -> JSONResponse:
    """
    Query the RAG system with semantic search.
    
    This endpoint:
    1. Accepts a natural language query from authenticated user
    2. Retrieves relevant documents from ChromaDB using vector similarity
    3. Passes context to LLM for generation
    4. Returns AI-generated answer
    
    Args:
        data (AskRequest): User query
        token (str): JWT token (auto-injected via OAuth2)
        
    Returns:
        JSONResponse: {"answer": "<generated_response>"}
        
    Raises:
        HTTPException: 400 if query is empty
        HTTPException: 401 if token is invalid
        HTTPException: 500 if RAG processing fails
        
    Vector Search Flow:
    1. Embed query using embedding service
    2. Search ChromaDB for top-k similar documents
    3. Combine documents as context for LLM
    4. LLM generates answer based on context
    """
    query = data.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Process query through RAG pipeline (now async)
        answer = await ask_rag_async(query)
        return JSONResponse(content={"answer": answer}, media_type="application/json; charset=utf-8")
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Error in /ask endpoint: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {exc}")
