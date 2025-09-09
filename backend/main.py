from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
import asyncio
import threading
import tempfile

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_FILE = os.path.join(BASE_DIR, "documents.json")

BACKUP_DIR_NAME = "backups"
_file_lock = threading.RLock()


def _ensure_backup_dir_exists(base_path: str):
    backup_dir = os.path.join(base_path, BACKUP_DIR_NAME)
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def _load_documents_sync() -> List[Document]:
    """Load documents from JSON file (synchronous, thread-safe)"""
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    try:
        with _file_lock:
            with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        return [Document(**doc) for doc in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


async def load_documents() -> List[Document]:
    """Async wrapper to load documents without blocking the event loop"""
    return await asyncio.to_thread(_load_documents_sync)


def _save_documents_sync(documents: List[Document]):
    """Save documents to JSON file atomically, then write a timestamped backup copy (synchronous, thread-safe for main file write)"""
    # Serialize once to keep main file and backup identical
    serialized = json.dumps([doc.model_dump() for doc in documents], default=str, indent=2)

    documents_dir = os.path.dirname(DOCUMENTS_FILE) or "."

    # Atomically write main file under lock to avoid readers seeing partial writes
    with _file_lock:
        fd, tmp_path = tempfile.mkstemp(dir=documents_dir, prefix="documents_", suffix=".json")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(serialized)
            os.replace(tmp_path, DOCUMENTS_FILE)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    # Prepare backup path alongside the main file (no lock needed)
    backup_dir = _ensure_backup_dir_exists(documents_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_filename = f"documents_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_filename)

    # Write backup file
    with open(backup_path, 'w', encoding='utf-8') as bf:
        bf.write(serialized)


async def save_documents(documents: List[Document]):
    """Async wrapper to save documents without blocking the event loop"""
    await asyncio.to_thread(_save_documents_sync, documents)

@app.get("/")
async def root():
    return {"message": "Shareboard API is running"}


@app.get("/api/documents", response_model=List[Document])
async def get_documents():
    """Get all documents"""
    return await load_documents()


@app.get("/api/documents/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """Get a specific document by ID"""
    documents = await load_documents()
    for doc in documents:
        if doc.id == document_id:
            return doc
    raise HTTPException(status_code=404, detail="Document not found")


@app.post("/api/documents", response_model=Document)
async def create_document(document: DocumentCreate):
    """Create a new document"""
    documents = await load_documents()

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
    await save_documents(documents)

    return new_document


@app.put("/api/documents/{document_id}", response_model=Document)
async def update_document(document_id: str, document_update: DocumentUpdate):
    """Update an existing document"""
    documents = await load_documents()

    for i, doc in enumerate(documents):
        if doc.id == document_id:
            # Update fields if provided
            if document_update.title is not None:
                doc.title = document_update.title
            if document_update.content is not None:
                doc.content = document_update.content
            doc.updated_at = datetime.now()

            documents[i] = doc
            await save_documents(documents)
            return doc

    raise HTTPException(status_code=404, detail="Document not found")


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    documents = await load_documents()

    for i, doc in enumerate(documents):
        if doc.id == document_id:
            documents.pop(i)
            await save_documents(documents)
            return {"message": "Document deleted successfully"}

    raise HTTPException(status_code=404, detail="Document not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)