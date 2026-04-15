import os
from app.rag import initialize_rag, ask_rag, CONFIG
print("Hackathon Quickstart")
print("Config:", CONFIG["title"])
initialize_rag()
print("Data ready:", DATA_READY)
print("Test query: What is the RAG status?")
print(ask_rag("status"))
print("✅ Backend ready! Run uvicorn app.main:app --reload")
print("Frontend: cd ../frontend && npm start")
print("Set .env with LLM_API_KEY, set LLM_PROVIDER=groq/openai")
print("Upload data via /upload endpoint")
