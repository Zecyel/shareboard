from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Shareboard API", description="API for shared document management")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vue dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Document model
class Document(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

class DocumentCreate(BaseModel):
    title: str
    content: str = ""

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# Simple file-based storage (in production, use a proper database)
DOCUMENTS_FILE = "documents.json"

def load_documents() -> List[Document]:
    """Load documents from JSON file"""
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    try:
        with open(DOCUMENTS_FILE, 'r') as f:
            data = json.load(f)
            return [Document(**doc) for doc in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_documents(documents: List[Document]):
    """Save documents to JSON file"""
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump([doc.model_dump() for doc in documents], f, default=str, indent=2)

@app.get("/")
async def root():
    return {"message": "Shareboard API is running"}

@app.get("/api/documents", response_model=List[Document])
async def get_documents():
    """Get all documents"""
    return load_documents()

@app.get("/api/documents/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """Get a specific document by ID"""
    documents = load_documents()
    for doc in documents:
        if doc.id == document_id:
            return doc
    raise HTTPException(status_code=404, detail="Document not found")

@app.post("/api/documents", response_model=Document)
async def create_document(document: DocumentCreate):
    """Create a new document"""
    documents = load_documents()
    
    # Generate simple ID (in production, use UUID or proper ID generation)
    doc_id = str(len(documents) + 1)
    now = datetime.now()
    
    new_document = Document(
        id=doc_id,
        title=document.title,
        content=document.content,
        created_at=now,
        updated_at=now
    )
    
    documents.append(new_document)
    save_documents(documents)
    
    return new_document

@app.put("/api/documents/{document_id}", response_model=Document)
async def update_document(document_id: str, document_update: DocumentUpdate):
    """Update an existing document"""
    documents = load_documents()
    
    for i, doc in enumerate(documents):
        if doc.id == document_id:
            # Update fields if provided
            if document_update.title is not None:
                doc.title = document_update.title
            if document_update.content is not None:
                doc.content = document_update.content
            doc.updated_at = datetime.now()
            
            documents[i] = doc
            save_documents(documents)
            return doc
    
    raise HTTPException(status_code=404, detail="Document not found")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    documents = load_documents()
    
    for i, doc in enumerate(documents):
        if doc.id == document_id:
            documents.pop(i)
            save_documents(documents)
            return {"message": "Document deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Document not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)