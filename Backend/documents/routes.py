from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from database import get_db
from documents.schema.dtos import DocumentResponseSchema, DocumentListResponseSchema, DocumentCreateSchema
from documents.services import DocumentService
from uuid import UUID
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponseSchema, status_code=201)
def create_document(
    title: str = Form(..., min_length=1, max_length=255),
    description: str | None = Form(None, max_length=1000),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Criar novo documento com upload de arquivo.
    
    - **title**: Título do documento (obrigatório)
    - **description**: Descrição opcional do documento
    - **file**: Arquivo PDF, PNG ou JPG (máx 10MB)
    """
    # Validar com schema (manualmente já que é Form)
    try:
        schema = DocumentCreateSchema(title=title, description=description)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    document = DocumentService.create_document(
        db=db,
        title=schema.title,
        description=schema.description,
        file=file
    )
    
    return document


@router.get("/", response_model=DocumentListResponseSchema)
def list_documents(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """
    Listar documentos com paginação.
    """
    documents, total = DocumentService.list_documents(db, page, page_size)
    
    import math
    total_pages = math.ceil(total / page_size)
    
    return {
        "documents": documents,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{document_id}", response_model=DocumentResponseSchema)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Buscar documento por ID.
    """
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return document

@router.get("/{document_id}/view")
def view_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Redireciona para a URL do Cloudinary para visualizar o arquivo no navegador
    """
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    return RedirectResponse(url=document.file_path)

@router.get("/{document_id}/download")
def download_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Força o download do arquivo (adiciona flag fl_attachment na URL do Cloudinary)
    """
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    download_url = document.file_path.replace("/upload/", "/upload/fl_attachment/")
    
    return RedirectResponse(url=download_url)