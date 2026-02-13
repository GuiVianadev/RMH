from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class CommentCreateSchema(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Conteúdo do comentário"
    )
    
    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Comentário não pode ser vazio ou apenas espaços')
        return v.strip()


class CommentResponseSchema(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CommentListResponseSchema(BaseModel):
    comments: list[CommentResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int