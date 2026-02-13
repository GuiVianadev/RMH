from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime

class DocumentCreateSchema(BaseModel):
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Título do documento"
    )
    description: str | None = Field(
        None, 
        max_length=1000,
        description="Descrição opcional do documento"
    )
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Título não pode ser vazio ou apenas espaços')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def description_strip(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class DocumentResponseSchema(BaseModel):
    id: UUID
    title: str
    description: str | None
    file_path: str
    file_type: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentListResponseSchema(BaseModel):
    documents: list[DocumentResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int