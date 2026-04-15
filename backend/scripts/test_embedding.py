import os
from dotenv import load_dotenv
from pathlib import Path
from app.config import config
from openai import OpenAI

load_dotenv()

print("Testing embedding API...")
print(f"Model: {config.EMBEDDING_MODEL}")
print(f"Base URL: {config.EMBEDDING_BASE_URL}")
print(f"API Key set: {'yes' if config.EMBEDDING_API_KEY else 'no'}")

client = OpenAI(
    api_key=config.EMBEDDING_API_KEY,
    base_url=config.EMBEDDING_BASE_URL,
    default_headers={"Content-Type": "application/json"}
)

try:
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input="test query",
    )
    print("✅ Embedding success!")
    print(f"Dimension: {len(response.data[0].embedding)}")
except Exception as exc:
    print(f"❌ Embedding error: {exc}")

