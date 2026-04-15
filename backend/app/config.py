import os
import logging
import uuid
from pathlib import Path
from dotenv import load_dotenv

def setup_logging(level="INFO"):
    lgr = logging.getLogger("rag_hackathon")
    lgr.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not lgr.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"))
        lgr.addHandler(h)
    return lgr

logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))
load_dotenv()

def get_llm_config(provider=None):
    provider = provider or os.getenv("LLM_PROVIDER", "openai").lower()
    
    configs = {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "api_key": os.getenv("LLM_API_KEY", "")
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "model": os.getenv("LLM_MODEL", "llama-3.1-70b-versatile"),
            "api_key": os.getenv("LLM_API_KEY", "")
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "model": os.getenv("LLM_MODEL", "llama3.2"),
            "api_key": "ollama"  # not needed
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1",
            "model": os.getenv("LLM_MODEL", "claude-3-5-sonnet-20240620"),
            "api_key": os.getenv("LLM_API_KEY", "")
        },
        "tcs": {  # keep for backward
            "base_url": "https://genailab.tcs.in",
            "model": "azure/genailab-maas-gpt-4o",
            "api_key": os.getenv("LLM_API_KEY", "")
        }
    }
    return configs.get(provider, configs["openai"])

llm_config = get_llm_config()

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
if EMBEDDING_PROVIDER == "openai":
    EMBEDDING_BASE_URL = "https://api.openai.com/v1"
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")
else:
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "hackathon")
DATA_DIR = os.getenv("DATA_DIR", "./data")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

config = {
    "llm": llm_config,
    "embedding": {
        "base_url": EMBEDDING_BASE_URL,
        "model": EMBEDDING_MODEL,
        "api_key": EMBEDDING_API_KEY
    },
    "chroma": {
        "persist_dir": CHROMA_PERSIST_DIR,
        "collection": CHROMA_COLLECTION
    },
    "data_dir": DATA_DIR,
    "verify_ssl": VERIFY_SSL,
    "demo_mode": DEMO_MODE
}

def generate_session_id():
    return str(uuid.uuid4())

DOMAIN_KEYWORDS = {"query","question","help","information","data","details","explain","what","how","when","where","why","tell me","show me","find","search","lookup","check","status","update","create","delete","modify","change","add","remove","list","view","display","report","summary","overview","analysis","insights","recommendations","suggestions","advice","guidance","support","assistance","help me","i need","please","can you","would you","could you"}

def is_domain_relevant(msg):
    lo = msg.lower()
    if any(k in lo for k in DOMAIN_KEYWORDS):
        return True
    if len(msg.split()) <= 4:
        return True
    return False

def log_audit_event(action="", applicant_id=None, user_role=None, model_used="", decision=None, details=None):
    logger.info(f"AUDIT: {action} | {applicant_id} | {model_used}")
    return {}
