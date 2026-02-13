import uuid
from typing import Sequence
from contextlib import contextmanager

from fastapi import UploadFile, HTTPException
from sqlalchemy import exists, select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .schema.dtos import DocumentResponseSchema
from .models import Document
import cloudinary
import cloudinary.uploader
from config import settings


cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024 


class DocumentService:
    
    @staticmethod
    @contextmanager
    def _upload_transaction(db: Session, cloudinary_id: str):
        """Gerencia transação: rollback no DB + limpeza no Cloudinary se falhar"""
        try:
            yield
            db.commit()
        except IntegrityError as e:
            db.rollback()
            cloudinary.uploader.destroy(cloudinary_id)
            
            if 'title' in str(e.orig).lower():
                raise HTTPException(status_code=409, detail="Título já existe")
            raise HTTPException(status_code=500, detail="Erro de integridade")
            
        except Exception as e:
            db.rollback()
            cloudinary.uploader.destroy(cloudinary_id)
            raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")
    
    @staticmethod
    def create_document(
        db: Session,
        title: str,
        description: str | None,
        file: UploadFile,
    ) -> Document:
        """
        Cria um novo documento, realizando upload e persistência de metadados.

        Valida o tipo e tamanho do arquivo, verifica se o título é único,
        realiza o upload para o Cloudinary e salva o registro no banco.
        """
        if db.scalar(select(exists().where(Document.title == title))):
            raise HTTPException(status_code=409, detail="Título já existe")
        
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Tipo não permitido. Use PDF, PNG ou JPG")
        
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")

        file_id = str(uuid.uuid4())
        file_extension = ALLOWED_TYPES[file.content_type]

        upload_result = cloudinary.uploader.upload(
            content,
            public_id=file_id,
            resource_type="image",
            folder="documents",
            format=file_extension
        )
            
        with DocumentService._upload_transaction(db, upload_result['public_id']):
            document = Document(
                title=title,
                description=description,
                file_path=upload_result['secure_url'],
                file_type=file_extension,
                cloudinary_id=upload_result['public_id']
            )
            
            db.add(document)
            db.flush()
            db.refresh(document)
            
            DocumentResponseSchema.model_validate(document)

        return document

    @staticmethod
    def list_documents(
        db: Session,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[Sequence[Document], int]:
        """Lista documentos de forma paginada, ordenados por data de criação (desc)."""
        if page < 1:
            page = 1

        offset = (page - 1) * page_size

        stmt = (
            select(Document)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        documents = db.execute(stmt).scalars().all()

        total = db.scalar(select(func.count()).select_from(Document))

        return documents, total
    
    @staticmethod
    def get_document(db: Session, document_id: uuid.UUID) -> Document | None:
        """Busca um documento específico pelo ID."""
        return db.scalar(select(Document).where(Document.id == document_id))
    
    @staticmethod
    def delete_document(db: Session, document_id: uuid.UUID) -> bool:
        """Deletar documento do banco e do Cloudinary"""
        document = DocumentService.get_document(db, document_id)
        if not document:
            return False
        
        try:
            resource_type = "raw" if document.file_type == "pdf" else "image"
            cloudinary.uploader.destroy(public_id=document.cloudinary_id, resource_type=resource_type, invalidate=True)
        except Exception as e:
            print(f"Erro ao deletar do Cloudinary: {e}")
        
        db.delete(document)
        db.commit()
        return True
    
