from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.graph import run_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    content: str

@app.get("/")
def root():
    return {
        "message": "ErrorID API Running"
    }

@app.post("/analyze")
def analyze(data: AnalyzeRequest):
    return run_graph(data.content)