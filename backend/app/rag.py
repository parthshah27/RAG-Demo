import glob
import json
import os
from pathlib import Path

import chromadb
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / ".chroma"

CONFIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)


def load_config():
    """Load config from environment or find in config folder."""
    config_file = os.getenv("CONFIG_FILE")

    if config_file:
        if not config_file.endswith(".json"):
            config_file = f"{config_file}.json"

        config_path = CONFIG_DIR / config_file
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as file:
                print(f"Loaded config from config/{config_file}")
                return json.load(file)

        fallback_path = Path(config_file)
        if fallback_path.exists():
            with open(fallback_path, "r", encoding="utf-8") as file:
                print(f"Loaded config from {config_file}")
                return json.load(file)

    default_config = CONFIG_DIR / "config.json"
    if default_config.exists():
        with open(default_config, "r", encoding="utf-8") as file:
            print("Loaded config from config/config.json")
            return json.load(file)

    print("No config file found. Using generic defaults.")
    return {
        "domain": "general",
        "title": "AI Assistant",
        "description": "Multi-purpose AI RAG Assistant",
        "system_prompt": (
            "You are a helpful AI assistant. Use the provided context to answer "
            "questions accurately and concisely."
        ),
        "query_enhancement_prompt": (
            "Focus on providing relevant and actionable information based on the context."
        ),
        "data_paths": ["data/*.csv"],
        "demo_responses": {},
    }


CONFIG = load_config()

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
COLLECTION_NAME = f"{CONFIG['domain'].replace(' ', '_').lower()}_rag"
collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

print(f"Using persistent ChromaDB at: {CHROMA_DIR}")
print(f"Collection: {COLLECTION_NAME}")

DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() == "true"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DATA_READY = False


def get_embedding(text):
    """Get embeddings with fallback for API errors."""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        return response.data[0].embedding
    except Exception as exc:
        print(f"Embedding error: {exc}")
        return [0.0] * 1536


def load_data():
    """Load and index data from configured paths."""
    global DATA_READY

    try:
        existing_count = collection.count()
        if existing_count > 0:
            print(f"Collection already indexed with {existing_count} documents")
            DATA_READY = True
            return
    except Exception:
        pass

    all_files = []
    default_paths = ["data/*.csv", "data/**/*.csv"]
    configured_paths = CONFIG.get("data_paths", default_paths)

    for path_pattern in configured_paths:
        if not Path(path_pattern).is_absolute():
            full_pattern = str(BASE_DIR / path_pattern)
        else:
            full_pattern = path_pattern

        all_files.extend(glob.glob(full_pattern, recursive=True))

    if not all_files:
        print(f"No data files found in: {configured_paths}")
        print(f"Searched in: {BASE_DIR}")
        DATA_READY = False
        return

    print(f"Found {len(all_files)} data file(s)")

    documents = []
    ids = []
    idx = 0
    skipped = 0

    for file_path in all_files:
        try:
            print(f"Processing: {Path(file_path).name}...", end=" ")
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding="latin-1")
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding="cp1252")

            df.columns = [col.strip().replace(" ", "_") for col in df.columns]

            for _, row in df.iterrows():
                text_parts = []
                for col in df.columns:
                    value = row[col]
                    if pd.notna(value):
                        text_parts.append(f"{col}:{value}")

                text = " | ".join(text_parts)
                documents.append(text)
                ids.append(f"{Path(file_path).stem}_{idx}")
                idx += 1

            print(f"{idx} records")
        except Exception as exc:
            print(f"Error: {exc}")
            skipped += 1

    if not documents:
        print("No documents loaded from data files")
        DATA_READY = False
        return

    print(f"Creating {len(documents)} embeddings...")

    batch_size = 50
    embeddings = []
    for start in range(0, len(documents), batch_size):
        batch = documents[start:start + batch_size]
        batch_embeddings = [get_embedding(doc) for doc in batch]
        embeddings.extend(batch_embeddings)
        processed = min(start + batch_size, len(documents))
        if processed % 200 == 0 or processed == len(documents):
            print(f"Embeddings ready: {processed}/{len(documents)}")

    collection.add(documents=documents, embeddings=embeddings, ids=ids)

    print(f"Indexed {len(documents)} {CONFIG['domain']} records")
    if skipped > 0:
        print(f"Skipped {skipped} files")
    DATA_READY = True



def initialize_rag():
    """Ensure the vector store is ready before serving requests."""
    global DATA_READY
    if DATA_READY:
        return

    try:
        load_data()
    except Exception as exc:
        DATA_READY = False
        print(f"Warning: Could not load data on startup: {exc}")
        print("The RAG system may not work properly.")



def ask_rag(query):
    if DEMO_MODE:
        query_lower = query.lower()
        demo_responses = CONFIG.get("demo_responses", {})

        for key, response in demo_responses.items():
            if key in query_lower:
                return response

        return (
            f"Demo mode: This is a sample response for '{query}' in "
            f"{CONFIG['domain'].title()} domain. Please set up your OpenAI API key "
            "and set DEMO_MODE=False to get real answers."
        )

    if not DATA_READY:
        raise RuntimeError(
            "Knowledge base is not ready. Please verify the configured data files and restart the backend."
        )

    try:
        enhanced_query = f"""
User is asking about {CONFIG['domain']} data.
Query: {query}
{CONFIG.get('query_enhancement_prompt', '')}
"""

        query_embedding = get_embedding(enhanced_query)
        results = collection.query(query_embeddings=[query_embedding], n_results=5)

        documents = results.get("documents") or []
        context = "\n\n".join(documents[0]) if documents and documents[0] else "No data available"

        prompt = f"""
{CONFIG.get('system_prompt', 'You are a helpful AI assistant.')}

Context:
{context}

Question:
{query}

Answer in a clear sentence:
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return response.choices[0].message.content

    except Exception as exc:
        error_msg = str(exc)
        lowered_error = error_msg.lower()
        if "quota" in lowered_error or "429" in lowered_error:
            raise Exception(
                "OpenAI API quota exceeded. Please check your API key and billing or enable DEMO_MODE=True."
            )
        if "authentication" in lowered_error or "401" in lowered_error:
            raise Exception("Invalid OpenAI API key. Please check your .env file.")
        raise Exception(f"Error processing query: {error_msg}")


if __name__ == "__main__":
    initialize_rag()
    while True:
        q = input("\nAsk: ")
        print("\nAI:", ask_rag(q))
