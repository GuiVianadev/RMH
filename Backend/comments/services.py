import uuid
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select, func, exists
from sqlalchemy.orm import Session

from .schema.dtos import CommentResponseSchema
from .models import Comment
from documents.models import Document 


class CommentService:
    
    @staticmethod
    def create_comment(
        db: Session,
        document_id: uuid.UUID,
        content: str,
    ) -> Comment:
        """Criar novo comentário em um documento"""
        
        if not db.scalar(select(exists().where(Document.id == document_id))):
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        comment = Comment(
            document_id=document_id,
            content=content
        )
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        CommentResponseSchema.model_validate(comment)
        
        return comment
    
    @staticmethod
    def list_comments(
        db: Session,
        document_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Comment], int]:
        """Listar comentários de um documento com paginação"""
        
        if not db.scalar(select(exists().where(Document.id == document_id))):
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        if page < 1:
            page = 1

        offset = (page - 1) * page_size

        stmt = (
            select(Comment)
            .where(Comment.document_id == document_id)
            .order_by(Comment.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        comments = db.execute(stmt).scalars().all()

        total = db.scalar(
            select(func.count())
            .select_from(Comment)
            .where(Comment.document_id == document_id)
        )

        return comments, total
    
    @staticmethod
    def get_comment(
        db: Session,
        comment_id: uuid.UUID,
        document_id: uuid.UUID | None = None
    ) -> Comment | None:
        """Buscar comentário por ID (opcionalmente validando documento)"""
        stmt = select(Comment).where(Comment.id == comment_id)
        
        if document_id:
            stmt = stmt.where(Comment.document_id == document_id)
        
        return db.scalar(stmt)