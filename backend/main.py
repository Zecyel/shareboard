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
import shutil
import requests

app = FastAPI(title="Shareboard API", description="API for shared document management")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3005"],  # Vue dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Document model - 更新为只包含元数据，内容从文件读取
class Document(BaseModel):
    id: str
    title: str
    content: str  # 这个字段在API响应时会从文件读取
    created_at: datetime
    updated_at: datetime

class DocumentMeta(BaseModel):
    """文档元数据，存储在documents.json中"""
    id: str
    title: str
    file_path: str  # 文件路径
    created_at: datetime
    updated_at: datetime

class DocumentCreate(BaseModel):
    title: str
    content: str = ""

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class LitexCodeRequest(BaseModel):
    code: str

class LitexCodeResponse(BaseModel):
    result: str

# 文件存储配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_FILE = os.path.join(BASE_DIR, "documents.json")
FILES_DIR = os.path.join(BASE_DIR, "file")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

_file_lock = threading.RLock()

def _ensure_dirs_exist():
    """确保所需目录存在"""
    os.makedirs(FILES_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def _get_file_path(doc_id: str) -> str:
    """获取文档文件路径"""
    return os.path.join(FILES_DIR, f"{doc_id}.lix")

def _get_backup_path(doc_id: str) -> str:
    """获取备份文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return os.path.join(BACKUP_DIR, f"{doc_id}.{timestamp}.lix")

def _load_document_metas_sync() -> List[DocumentMeta]:
    """从JSON文件加载文档元数据"""
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    try:
        with _file_lock:
            with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        return [DocumentMeta(**meta) for meta in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _save_document_metas_sync(metas: List[DocumentMeta]):
    """保存文档元数据到JSON文件"""
    with _file_lock:
        # 原子写入
        fd, tmp_path = tempfile.mkstemp(dir=BASE_DIR, prefix="documents_", suffix=".json")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump([meta.model_dump() for meta in metas], f, default=str, indent=2)
            os.replace(tmp_path, DOCUMENTS_FILE)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

def _read_file_content_sync(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        return ""

def _write_file_content_sync(file_path: str, content: str):
    """写入文件内容"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def _backup_file_sync(source_path: str, backup_path: str):
    """备份文件"""
    if os.path.exists(source_path):
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(source_path, backup_path)

async def load_documents() -> List[Document]:
    """加载所有文档（包含内容）"""
    def _load():
        _ensure_dirs_exist()
        metas = _load_document_metas_sync()
        documents = []
        
        for meta in metas:
            content = _read_file_content_sync(meta.file_path)
            doc = Document(
                id=meta.id,
                title=meta.title,
                content=content,
                created_at=meta.created_at,
                updated_at=meta.updated_at
            )
            documents.append(doc)
        
        return documents
    
    return await asyncio.to_thread(_load)

async def get_document_by_id(doc_id: str) -> Optional[Document]:
    """根据ID获取单个文档"""
    def _get():
        _ensure_dirs_exist()
        metas = _load_document_metas_sync()
        
        for meta in metas:
            if meta.id == doc_id:
                content = _read_file_content_sync(meta.file_path)
                return Document(
                    id=meta.id,
                    title=meta.title,
                    content=content,
                    created_at=meta.created_at,
                    updated_at=meta.updated_at
                )
        return None
    
    return await asyncio.to_thread(_get)

async def save_document(document: Document, is_new: bool = False):
    """保存文档（内容和元数据）"""
    def _save():
        _ensure_dirs_exist()
        
        # 准备文件路径
        file_path = _get_file_path(document.id)
        
        # 如果是更新操作，先备份原文件
        if not is_new and os.path.exists(file_path):
            backup_path = _get_backup_path(document.id)
            _backup_file_sync(file_path, backup_path)
        
        # 写入文件内容
        _write_file_content_sync(file_path, document.content)
        
        # 更新元数据
        metas = _load_document_metas_sync()
        
        # 创建或更新元数据
        meta = DocumentMeta(
            id=document.id,
            title=document.title,
            file_path=file_path,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
        
        # 查找现有元数据并更新，或添加新的
        updated = False
        for i, existing_meta in enumerate(metas):
            if existing_meta.id == document.id:
                metas[i] = meta
                updated = True
                break
        
        if not updated:
            metas.append(meta)
        
        # 保存元数据
        _save_document_metas_sync(metas)
    
    await asyncio.to_thread(_save)

async def delete_document_by_id(doc_id: str) -> bool:
    """删除文档"""
    def _delete():
        _ensure_dirs_exist()
        metas = _load_document_metas_sync()
        
        # 查找并删除元数据
        for i, meta in enumerate(metas):
            if meta.id == doc_id:
                # 备份文件
                if os.path.exists(meta.file_path):
                    backup_path = _get_backup_path(doc_id)
                    _backup_file_sync(meta.file_path, backup_path)
                    # 删除原文件
                    try:
                        os.remove(meta.file_path)
                    except OSError:
                        pass
                
                # 删除元数据
                metas.pop(i)
                _save_document_metas_sync(metas)
                return True
        
        return False
    
    return await asyncio.to_thread(_delete)

# API路由
@app.get("/")
async def root():
    return {"message": "Shareboard API is running"}

@app.get("/api/documents", response_model=List[Document])
async def get_documents():
    """获取所有文档"""
    return await load_documents()

@app.get("/api/documents/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """获取特定文档"""
    document = await get_document_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.post("/api/documents", response_model=Document)
async def create_document(document: DocumentCreate):
    """创建新文档"""
    # 生成文档ID
    existing_docs = await load_documents()
    doc_id = str(len(existing_docs) + 1)
    
    now = datetime.now()
    new_document = Document(
        id=doc_id,
        title=document.title,
        content=document.content,
        created_at=now,
        updated_at=now
    )
    
    await save_document(new_document, is_new=True)
    return new_document

@app.put("/api/documents/{document_id}", response_model=Document)
async def update_document(document_id: str, document_update: DocumentUpdate):
    """更新文档"""
    existing_doc = await get_document_by_id(document_id)
    if existing_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 更新字段
    updated_doc = existing_doc.model_copy()
    if document_update.title is not None:
        updated_doc.title = document_update.title
    if document_update.content is not None:
        updated_doc.content = document_update.content
    updated_doc.updated_at = datetime.now()
    
    await save_document(updated_doc, is_new=False)
    return updated_doc

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """删除文档"""
    success = await delete_document_by_id(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

@app.post("/api/run-litex", response_model=LitexCodeResponse)
async def run_litex_code(request: LitexCodeRequest):
    """运行 Litex 代码"""
    try:
        response = await asyncio.to_thread(
            requests.post,
            "https://litexlang.org/api/litex",
            json={
                "targetFormat": "Run Litex",
                "litexString": request.code
            }
        )
        
        if not response.ok:
            return LitexCodeResponse(result=f"Network Error: {response.status_text}")
        
        data = response.json()
        return LitexCodeResponse(result=data.get("data", "No result"))
        
    except Exception as error:
        return LitexCodeResponse(result=f"Error: {str(error)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)