import glob
import json
import os
from pathlib import Path
from typing import Any, Dict

import chromadb
import pandas as pd
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from .config import config, logger

# Ensure directories exist
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = Path(config["chroma"]["persist_dir"])

CONFIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_text_list(value, fallback):
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return fallback


def _normalize_dashboard(domain_config: Dict[str, Any]) -> Dict[str, Any]:
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

def load_config():
    """Load domain-specific config."""
    config_file = os.getenv("CONFIG_FILE")
    if config_file:
        if not config_file.endswith(".json"):
            config_file += ".json"
        config_path = CONFIG_DIR / config_file
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as file:
                logger.info(f"Loaded config from {config_file}")
                return normalize_config(json.load(file))
    
    # Fallback to default
    default_config = CONFIG_DIR / "config.json"
    if default_config.exists():
        with open(default_config, "r", encoding="utf-8") as file:
            logger.info("Loaded default config")
            return normalize_config(json.load(file))
    
    logger.warning("No config found, using generic defaults")
    return normalize_config({
        "domain": "general",
        "title": "RAG Assistant",
        "system_prompt": "You are a helpful AI assistant with access to specific data context.",
        "data_paths": ["data/*.csv"]
    })

CONFIG = load_config()


def get_collection_name() -> str:
    configured_name = str(config["chroma"]["collection"]).strip()
    domain = CONFIG.get("domain", "general")
    return f"{configured_name}_{domain}"

# ChromaDB setup
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
COLLECTION_NAME = get_collection_name()


def get_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


collection = get_collection()

logger.info(f"ChromaDB ready: {CHROMA_DIR}, Collection: {COLLECTION_NAME}")

# LLM and embedding clients
client = OpenAI(
    api_key=config["llm"]["api_key"],
    base_url=config["llm"]["base_url"]
)
embedding_client = OpenAI(
    api_key=config["embedding"]["api_key"],
    base_url=config["embedding"]["base_url"]
)

DATA_READY = False
sentence_model = None

def get_embedding(text: str):
    """Generate embedding with API fallback to local model."""
    try:
        response = embedding_client.embeddings.create(
            model=config["embedding"]["model"],
            input=text[:8000],  # Truncate long texts
        )
        return response.data[0].embedding
    except Exception as exc:
        logger.warning(f"Embedding API error: {exc}, using local fallback")
        global sentence_model
        if sentence_model is None:
            logger.info("Loading sentence-transformers model...")
            sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = sentence_model.encode([text])[0].tolist()
        # Pad to match OpenAI dim (1536)
        emb_padded = emb + [0.0] * (1536 - len(emb))
        return emb_padded

def load_data():
    """Index CSV data files into ChromaDB."""
    global DATA_READY
    
    try:
        if collection.count() > 0:
            logger.info(f"Using existing index ({collection.count()} docs)")
            DATA_READY = True
            return
    except:
        pass
    
    all_files = []
    data_paths = CONFIG.get("data_paths", ["data/*.csv"])
    for pattern in data_paths:
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
    
    for file_path in all_files:
        try:
            df = pd.read_csv(file_path)
            df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
            for _, row in df.iterrows():
                parts = [f"{c}:{row[c]}" for c in df.columns if pd.notna(row[c])]
                doc = " | ".join(parts)
                if doc.strip():
                    documents.append(doc)
                    ids.append(f"doc_{idx_counter}")
                    idx_counter += 1
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    if documents:
        embeddings = [get_embedding(doc) for doc in documents]
        get_collection().add(documents=documents, embeddings=embeddings, ids=ids)
        logger.info(f"Indexed {len(documents)} documents")
        DATA_READY = True
    else:
        logger.error("No documents to index")
        DATA_READY = False

def initialize_rag():
    """Initialize data index on startup."""
    if DATA_READY:
        return
    load_data()

def ask_rag(query: str):
    """Main RAG query function."""
    if config.get("demo_mode", False):
        return f"DEMO: Sample response for '{query}' in {CONFIG.get('domain', 'general')} domain."
    
    if not DATA_READY:
        raise RuntimeError("Knowledge base not ready. Run load_data() first.")
    
    # Query ChromaDB
    query_emb = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=5
    )
    
    context_docs = results["documents"][0] if results["documents"] else []
    context = "\n\n".join(context_docs) if context_docs else "No relevant data found."
    
    prompt = f"""System instructions:
{CONFIG.get("system_prompt", "Answer accurately using the provided context only.")}

Context from {CONFIG.get('domain', 'data')}:
{context}

Question: {query}

Provide a concise, accurate answer:"""
    
    response = client.chat.completions.create(
        model=config["llm"]["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()

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
