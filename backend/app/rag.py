"""
RAG (Retrieval Augmented Generation) Module

Core RAG Pipeline Implementation:
1. DATA LOADING: Index CSV files into ChromaDB vector store
2. EMBEDDING: Convert text to vectors (OpenAI API with local fallback)
3. RETRIEVAL: Find similar documents using semantic search in ChromaDB
4. GENERATION: Use LLM to generate answers based on retrieved context

Vector Database Choice:
- Selected: ChromaDB (lightweight, persistent, built-in embedding support)
- Stores: Document embeddings and original text for semantic search
- Metadata: Stored with cosine distance metric for similarity
- Alternative: Could use Pinecone, Weaviate, Milvus for enterprise scale

LLM Integration:
- Primary: OpenAI-compatible API (configurable provider: OpenAI, Groq, Ollama, Anthropic)
- Embedding Model: Supports enterprise embedding services with local fallback
- Temperature: Set to 0.1 for deterministic, factual responses
"""

import asyncio
import glob
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import chromadb
import pandas as pd
from openai import OpenAI, AsyncOpenAI
from sentence_transformers import SentenceTransformer

from .config import config, logger

# ============================================================================
# DIRECTORY SETUP
# ============================================================================
# Ensure required directories exist
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = Path(config["chroma"]["persist_dir"])

CONFIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# CONFIG NORMALIZATION HELPERS
# ============================================================================

def _normalize_text_list(value, fallback):
    """
    Normalize a configuration value to a list of non-empty strings.
    
    Args:
        value: Input value (may be list, string, or None)
        fallback: Default list if value is invalid
        
    Returns:
        list: Cleaned list of strings, or fallback if invalid
    """
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return fallback


def _normalize_dashboard(domain_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build dashboard metrics and insights configuration with fallbacks.
    
    Args:
        domain_config: Domain-specific configuration dict
        
    Returns:
        dict: Dashboard config with "metrics" and "insights" lists
    """
    # Fallback metrics shown if domain doesn't provide custom ones
    fallback_metrics = [
        {"label": f"{domain_config['domain'].title()} Coverage", "value": "Ready", "change": "Live"},
        {"label": "Indexed Sources", "value": "Auto-detected", "change": "Config-driven"},
        {"label": "Assistant Mode", "value": "Domain aware", "change": "Adaptive"},
        {"label": "Contest Readiness", "value": "High", "change": "Flexible"},
    ]
    fallback_insights = [
        {
            "title": "Rapid Setup",
            "description": f"Switch the assistant to {domain_config['domain']} by updating config and data paths only.",
        },
        {
            "title": "Reusable Workflow",
            "description": "Landing page, chat prompts, uploads, and retrieval behavior are all driven by the active config.",
        },
        {
            "title": "Live Contest Friendly",
            "description": "You can onboard a new dataset quickly without rebuilding the frontend for each domain.",
        },
    ]

    dashboard = domain_config.get("dashboard")
    if not isinstance(dashboard, dict):
        dashboard = {}

    metrics = dashboard.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        metrics = domain_config.get("dashboard_metrics")
    if not isinstance(metrics, list) or not metrics:
        metrics = fallback_metrics

    insights = dashboard.get("insights")
    if not isinstance(insights, list) or not insights:
        insights = domain_config.get("insights")
    if not isinstance(insights, list) or not insights:
        insights = fallback_insights

    return {"metrics": metrics, "insights": insights}


def _build_ui_config(domain_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build frontend UI configuration from domain config.
    
    Constructs placeholders, sample queries, allowed file types, and dashboard config
    with intelligent fallbacks for missing values.
    
    Args:
        domain_config: Domain-specific configuration dict
        
    Returns:
        dict: Complete UI configuration for frontend
    """
    domain_name = domain_config.get("domain", "general")
    title = domain_config.get("title", "RAG Assistant")
    sample_queries = domain_config.get("sample_queries")
    if not isinstance(sample_queries, list) or not sample_queries:
        sample_queries = [
            f"What are the most important trends in this {domain_name} dataset?",
            f"Summarize the key insights for {domain_name}.",
            "Which patterns or anomalies should I focus on first?",
        ]

    allowed_file_types = _normalize_text_list(
        domain_config.get("allowed_file_types"),
        [".csv", ".txt", ".pdf", ".md"],
    )
    dashboard = _normalize_dashboard(domain_config)

    return {
        "chat_placeholder": domain_config.get("chat_placeholder", f"Ask about {domain_name}..."),
        "upload_prompt": domain_config.get("upload_prompt", "Analyze this file"),
        "sample_queries": sample_queries,
        "allowed_file_types": allowed_file_types,
        "empty_state_title": domain_config.get("empty_state_title", f"Welcome to {title}!"),
        "empty_state_description": domain_config.get(
            "empty_state_description",
            f"Ask questions, upload files, and explore insights for the {domain_name} domain.",
        ),
        "dashboard": dashboard,
    }


def normalize_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate domain configuration with sensible defaults.
    
    Args:
        raw_config: Raw config dict from JSON file
        
    Returns:
        dict: Normalized config with all required keys and proper types
    """
    domain_config = dict(raw_config or {})
    domain_config["domain"] = str(domain_config.get("domain", "general")).strip().lower() or "general"
    domain_config["title"] = domain_config.get("title", "RAG Assistant")
    domain_config["description"] = domain_config.get(
        "description",
        f"Analyze {domain_config['domain']} data with AI-powered insights",
    )
    domain_config["system_prompt"] = domain_config.get(
        "system_prompt",
        "You are a helpful AI assistant with access to specific data context.",
    )
    domain_config["data_paths"] = _normalize_text_list(domain_config.get("data_paths"), ["data/*.csv"])
    domain_config["demo_responses"] = domain_config.get("demo_responses", {})
    domain_config["ui"] = _build_ui_config(domain_config)
    return domain_config


def load_config() -> Dict[str, Any]:
    """
    Load and normalize domain-specific configuration.
    
    Configuration Loading Priority:
    1. CONFIG_FILE environment variable (if set)
    2. config.json (default)
    3. Generic fallback configuration
    
    Returns:
        dict: Normalized configuration with all required fields
    """
    config_file = os.getenv("CONFIG_FILE")
    if config_file:
        if not config_file.endswith(".json"):
            config_file += ".json"
        config_path = CONFIG_DIR / config_file
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as file:
                logger.info(f"Loaded config from {config_file}")
                return normalize_config(json.load(file))
    
    # Fallback to default config.json
    default_config = CONFIG_DIR / "config.json"
    if default_config.exists():
        with open(default_config, "r", encoding="utf-8") as file:
            logger.info("Loaded default config")
            return normalize_config(json.load(file))
    
    # Generic fallback
    logger.warning("No config found, using generic defaults")
    return normalize_config({
        "domain": "general",
        "title": "RAG Assistant",
        "system_prompt": "You are a helpful AI assistant with access to specific data context.",
        "data_paths": ["data/*.csv"]
    })


CONFIG = load_config()


# ============================================================================
# VECTOR DATABASE SETUP (ChromaDB)
# ============================================================================
# Decision: ChromaDB selected as vector database
# Rationale: Lightweight, persistent, built-in embedding support, easy to setup
# Alternative options: Pinecone (cloud), Weaviate, Milvus (enterprise scale)

def get_collection_name() -> str:
    """
    Generate domain-specific collection name for ChromaDB.
    
    Naming format: "{base_collection}_{domain}"
    This allows multiple domains to coexist in same database.
    
    Returns:
        str: Collection name (e.g., "hackathon_healthcare", "hackathon_retail")
    """
    configured_name = str(config["chroma"]["collection"]).strip()
    domain = CONFIG.get("domain", "general")
    return f"{configured_name}_{domain}"


# Initialize ChromaDB persistent client
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
COLLECTION_NAME = get_collection_name()


def get_collection():
    """
    Get or create ChromaDB collection for storing embeddings.
    
    Uses cosine distance for similarity metric (good for embeddings).
    
    Returns:
        chromadb.Collection: Collection object for add/query operations
    """
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


collection = get_collection()
logger.info(f"ChromaDB initialized: {CHROMA_DIR}, Collection: {COLLECTION_NAME}")


# ============================================================================
# LLM AND EMBEDDING CLIENTS
# ============================================================================
# Primary LLM: OpenAI-compatible API (configurable - OpenAI, Groq, Ollama, Anthropic)
# Embedding Model: Supports enterprise embedding services with local fallback
# Strategy: Use API when available, fall back to local transformers model

# LLM Client: Used for generating answers
client = OpenAI(
    api_key=config["llm"]["api_key"],
    base_url=config["llm"]["base_url"]
)

# Async LLM Client for concurrent requests
async_client = AsyncOpenAI(
    api_key=config["llm"]["api_key"],
    base_url=config["llm"]["base_url"]
)

# Embedding Client: Used for converting text to vectors
embedding_client = OpenAI(
    api_key=config["embedding"]["api_key"],
    base_url=config["embedding"]["base_url"]
)

# Async Embedding Client
async_embedding_client = AsyncOpenAI(
    api_key=config["embedding"]["api_key"],
    base_url=config["embedding"]["base_url"]
)

# Global state tracking
DATA_READY = False  # Flag: indicates if knowledge base is loaded
sentence_model = None  # Local embedding model (loaded on demand as fallback)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def _retry_api_call(func, max_retries=3, delay=1.0):
    """
    Retry API calls with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {exc}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"API call failed after {max_retries} attempts: {exc}")
                raise last_exc

@lru_cache(maxsize=1000)
def get_embedding(text: str) -> list:
    """
    Generate embedding vector for text using API with local fallback.
    
    OPTIMIZATION: LRU cache for frequently embedded texts.
    
    Embedding Strategy:
    1. PRIMARY: Use embedding API (OpenAI, Groq, etc.) when available
    2. FALLBACK: Use local SentenceTransformer model if API fails
    
    The fallback ensures robustness even if external API is down.
    
    Args:
        text (str): Text to embed (will be truncated to 8000 chars)
        
    Returns:
        list: Embedding vector (1536-dimensional for OpenAI compatibility)
        
    Raises:
        None (uses fallback on error)
    """
    try:
        # Attempt API embedding
        response = embedding_client.embeddings.create(
            model=config["embedding"]["model"],
            input=text[:8000],  # Truncate long texts to avoid API limits
        )
        return response.data[0].embedding
    except Exception as exc:
        # Fallback to local model on API error
        logger.warning(f"Embedding API error: {exc}, using local fallback")
        global sentence_model
        if sentence_model is None:
            logger.info("Loading sentence-transformers model...")
            sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embedding locally
        emb = sentence_model.encode([text])[0].tolist()
        
        # Pad to match OpenAI dimension (1536) for consistency
        emb_padded = emb + [0.0] * (1536 - len(emb))
        return emb_padded


@lru_cache(maxsize=1000)
async def get_embedding_async(text: str) -> list:
    """
    Async version of get_embedding for concurrent processing.
    
    OPTIMIZATION: LRU cache + retry logic for reliability.
    
    Uses async OpenAI client for non-blocking API calls.
    """
    async def _embed():
        response = await async_embedding_client.embeddings.create(
            model=config["embedding"]["model"],
            input=text[:8000],  # Truncate long texts to avoid API limits
        )
        return response.data[0].embedding
    
    try:
        return await _retry_api_call(_embed)
    except Exception as exc:
        # Fallback to local model on API error (still sync for now)
        logger.warning(f"Embedding API error after retries: {exc}, using local fallback")
        global sentence_model
        if sentence_model is None:
            logger.info("Loading sentence-transformers model...")
            sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embedding locally
        emb = sentence_model.encode([text])[0].tolist()
        
        # Pad to match OpenAI dimension (1536) for consistency
        emb_padded = emb + [0.0] * (1536 - len(emb))
        return emb_padded


# ============================================================================
# DATA INDEXING (Vector Store Population)
# ============================================================================

def load_data():
    """
    Load and index CSV data files into ChromaDB vector store.
    
    Indexing Process:
    1. Check if data already indexed (skip if collection has docs)
    2. Find CSV files matching configured patterns
    3. Parse each CSV, convert rows to semi-structured text
    4. Generate embeddings for each row
    5. Add documents to ChromaDB with metadata
    
    This function is idempotent - running multiple times is safe.
    
    Raises:
        None (logs errors instead, sets DATA_READY flag)
    """
    global DATA_READY
    
    # Skip if already indexed
    try:
        if collection.count() > 0:
            logger.info(f"Using existing index ({collection.count()} docs)")
            DATA_READY = True
            return
    except:
        pass
    
    # Find all CSV files matching configured patterns
    all_files = []
    data_paths = CONFIG.get("data_paths", ["data/*.csv"])
    for pattern in data_paths:
        # Support both relative and absolute paths
        full_pattern = str(BASE_DIR / pattern) if not Path(pattern).is_absolute() else pattern
        all_files.extend(glob.glob(full_pattern, recursive=True))
    
    if not all_files:
        logger.warning("No data files found")
        DATA_READY = False
        return
    
    logger.info(f"Indexing {len(all_files)} files")
    documents = []
    ids = []
    idx_counter = 0
    
    # Process each CSV file
    for file_path in all_files:
        try:
            # Read CSV and normalize column names
            df = pd.read_csv(file_path)
            df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
            
            # Convert each row to a document (semi-structured format)
            for _, row in df.iterrows():
                # Format: "column1:value1 | column2:value2 | ..."
                parts = [f"{c}:{row[c]}" for c in df.columns if pd.notna(row[c])]
                doc = " | ".join(parts)
                if doc.strip():
                    documents.append(doc)
                    ids.append(f"doc_{idx_counter}")
                    idx_counter += 1
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    # Generate embeddings and add to vector store
    if documents:
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        
        # OPTIMIZATION: Batch embedding generation for better performance
        batch_size = 10  # Process in batches to avoid memory issues
        embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            try:
                # Try batch API embedding first
                response = embedding_client.embeddings.create(
                    model=config["embedding"]["model"],
                    input=[doc[:8000] for doc in batch_docs]  # Truncate each
                )
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as exc:
                logger.warning(f"Batch embedding failed: {exc}, falling back to individual processing")
                # Fallback to individual processing
                for doc in batch_docs:
                    embeddings.append(get_embedding(doc))
        
        get_collection().add(documents=documents, embeddings=embeddings, ids=ids)
        logger.info(f"Indexed {len(documents)} documents")
        DATA_READY = True
    else:
        logger.error("No documents to index")
        DATA_READY = False


# ============================================================================
# RAG INITIALIZATION AND QUERY PROCESSING
# ============================================================================

def initialize_rag():
    """
    Initialize RAG system on application startup.
    
    This function:
    1. Checks if knowledge base is already loaded
    2. Loads data into ChromaDB if needed
    3. Sets DATA_READY flag when complete
    
    Called once on app startup via lifespan manager.
    """
    if DATA_READY:
        return
    load_data()


def ask_rag(query: str) -> str:
    """
    Core RAG pipeline: Retrieve context from vector database, then generate answer with LLM.
    
    RAG Process:
    1. EMBED: Convert user query to vector
    2. RETRIEVE: Search ChromaDB for top-5 similar documents
    3. CONTEXT: Combine retrieved documents into context string
    4. GENERATE: Pass context to LLM to generate answer
    
    Args:
        query (str): User question in natural language
        
    Returns:
        str: AI-generated answer based on retrieved context
        
    Raises:
        RuntimeError: If knowledge base not ready (DATA_READY is False)
        
    LLM Configuration:
    - Temperature: 0.1 (low = deterministic, fact-based)
    - Max tokens: 500 (limits response length, ensures conciseness)
    - Model: Configurable via config (OpenAI, Groq, etc.)
    """
    # Demo mode: return canned response without querying data
    if config.get("demo_mode", False):
        return f"DEMO: Sample response for '{query}' in {CONFIG.get('domain', 'general')} domain."
    
    # Ensure knowledge base is loaded
    if not DATA_READY:
        raise RuntimeError("Knowledge base not ready. Run load_data() first.")
    
    # RETRIEVAL: Generate embedding for query and search ChromaDB
    query_emb = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=5  # Retrieve top 5 similar documents
    )
    
    # CONTEXT: Extract and combine retrieved documents
    context_docs = results["documents"][0] if results["documents"] else []
    context = "\n\n".join(context_docs) if context_docs else "No relevant data found."
    
    # GENERATION: Build prompt with context and query
    prompt = f"""System instructions:
{CONFIG.get("system_prompt", "Answer accurately using the provided context only.")}

Context from {CONFIG.get('domain', 'data')}:
{context}

Question: {query}

Provide a concise, accurate answer:"""
    
    # Call LLM to generate answer
    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,  # Low temperature for factual, deterministic responses
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()


async def ask_rag_async(query: str) -> str:
    """
    Async version of ask_rag for concurrent request handling.
    
    Uses async OpenAI clients for non-blocking API calls, improving
    concurrency and response times under load.
    """
    # Demo mode: return canned response without querying data
    if config.get("demo_mode", False):
        return f"DEMO: Sample response for '{query}' in {CONFIG.get('domain', 'general')} domain."
    
    # Ensure knowledge base is loaded
    if not DATA_READY:
        raise RuntimeError("Knowledge base not ready. Run load_data() first.")
    
    # RETRIEVAL: Generate embedding for query and search ChromaDB (async embedding)
    query_emb = await get_embedding_async(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=5  # Retrieve top 5 similar documents
    )
    
    # CONTEXT: Extract and combine retrieved documents
    context_docs = results["documents"][0] if results["documents"] else []
    context = "\n\n".join(context_docs) if context_docs else "No relevant data found."
    
    # GENERATION: Build prompt with context and query
    prompt = f"""System instructions:
{CONFIG.get("system_prompt", "Answer accurately using the provided context only.")}

Context from {CONFIG.get('domain', 'data')}:
{context}

Question: {query}

Provide a concise, accurate answer:"""
    
    # Call LLM to generate answer (async with retries)
    async def _generate():
        return await async_client.chat.completions.create(
            model=config["llm"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for factual, deterministic responses
            max_tokens=500
        )
    
    try:
        response = await _retry_api_call(_generate)
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error(f"LLM API error after retries: {exc}")
        raise RuntimeError(f"Failed to generate response: {exc}")


if __name__ == "__main__":
    initialize_rag()
    while True:
        query = input("\nQuery: ")
        if query.lower() in ["exit", "quit"]:
            break
        try:
            print("AI:", ask_rag(query))
        except Exception as e:
            print(f"Error: {e}")
