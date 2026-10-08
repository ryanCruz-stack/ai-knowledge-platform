from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.model import Document
import requests

app = FastAPI()

class DocumentCreate(BaseModel):
    title: str
    content: str

class DocumentUpdate(BaseModel):
    title: str
    content: str

class AskRequest(BaseModel):
    question: str

@app.post("/documents")
def create_document(document: DocumentCreate):
    db = SessionLocal()

    new_document = Document(
        title=document.title,
        content=document.content
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    db.close()

    return new_document

@app.get("/documents/{document_id}")
def get_documents(document_id: int):
    db = SessionLocal()

    document = db.get(Document, document_id)

    db.close()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document

@app.get("/documents")
def get_document():
    db = SessionLocal()

    documents = db.query(Document).all()

    db.close()

    return documents

@app.put("/documents/{document_id}")
def update_documents(document_id: int, document: DocumentUpdate):
    db = SessionLocal()

    existing_document = db.get(Document, document_id)

    if existing_document is None:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")

    existing_document.title = document.title
    existing_document.content = document.content

    db.commit()
    db.refresh(existing_document)

@app.delete("/documents/{document_id}")
def delete_document(document_id: int):
    db = SessionLocal()

    document = db.get(Document, document_id)

    if document is None:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()

    db.close()

    return {"message", "Document deleted"}

@app.post("/documents/{document_id}/ask")
def ask_document(document_id: int, request: AskRequest):
    db = SessionLocal()

    document = db.get(Document, document_id)

    db.close()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    prompt = f"""
    Answer the question using only the document below.
    
    DOCUMENT:
    {document.content}
    
    QUESTION:
    {request.question}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]