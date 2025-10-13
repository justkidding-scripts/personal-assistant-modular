#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
from assistant import Assistant

app = FastAPI()
assistant = Assistant()

class AskRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    return assistant.handle(req.query)
