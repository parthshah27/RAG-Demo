from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.auth import login_user
from app.rag import CONFIG, ask_rag, initialize_rag


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AskRequest(BaseModel):
    query: str = Field(min_length=1)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_rag()
    yield


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/config")
def get_config():
    """Get domain-specific configuration"""
    return JSONResponse(content=CONFIG, media_type="application/json; charset=utf-8")

@app.post("/login")
def login(data: LoginRequest):
    return login_user(data.username, data.password)

@app.post("/ask")
def ask(data: AskRequest):
    query = data.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        answer = ask_rag(query)
        return JSONResponse(content={"answer": answer}, media_type="application/json; charset=utf-8")
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Error in /ask endpoint: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {exc}")
