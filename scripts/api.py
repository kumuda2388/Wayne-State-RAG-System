from scripts.ask import ask_question
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI() #creates server opject

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask_api(query:Query):
    answer=ask_question(query.question)
    return {"answer":answer}