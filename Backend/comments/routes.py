from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from uuid import UUID
import math

from .services import CommentService
from .schema.dtos import (
    CommentCreateSchema,
    CommentResponseSchema,
    CommentListResponseSchema
)
from database import get_db


router = APIRouter(prefix="/documents/{document_id}/comments", tags=["comments"])


@router.post("/", response_model=CommentResponseSchema, status_code=201)
def create_comment(
    document_id: UUID,
    schema: CommentCreateSchema,
    db: Session = Depends(get_db),
):
    """
    Criar comentário em um documento
    
    - **document_id**: ID do documento
    - **content**: Conteúdo do comentário (1-5000 caracteres)
    """
    comment = CommentService.create_comment(
        db=db,
        document_id=document_id,
        content=schema.content
    )
    return comment


@router.get("/", response_model=CommentListResponseSchema)
def list_comments(
    document_id: UUID,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    Listar comentários de um documento com paginação
    
    - **document_id**: ID do documento
    - **page**: Página atual (padrão: 1)
    - **page_size**: Itens por página (padrão: 20, máx: 100)
    """
    if page_size > 100:
        page_size = 100
    
    comments, total = CommentService.list_comments(
        db=db,
        document_id=document_id,
        page=page,
        page_size=page_size
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return {
        "comments": comments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{comment_id}", response_model=CommentResponseSchema)
def get_comment(
    document_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Buscar comentário específico
    
    - **document_id**: ID do documento
    - **comment_id**: ID do comentário
    """
    comment = CommentService.get_comment(db, comment_id, document_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    return comment




