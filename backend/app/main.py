from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from .auth import login_user, SECRET, ALGORITHM

from .rag import CONFIG, ask_rag, initialize_rag
from .upload import router as upload_router





class LoginRequest(BaseModel):
    username: str
    password: str

class AskRequest(BaseModel):
    query: str = Field(min_length=1)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_rag()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(upload_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

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
    result = login_user(data.username, data.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@app.post("/ask")
def ask(data: AskRequest, token: str = Depends(verify_token)):
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
