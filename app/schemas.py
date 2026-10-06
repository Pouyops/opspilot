from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=1)


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    body: str
    status: str
    answer: str | None
    created_at: datetime

class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    source: str | None = Field(default=None, max_length=500)
    text: str = Field(min_length=1)


class DocumentRead(BaseModel):
    id: int
    title: str
    source: str | None
    created_at: datetime
    chunk_count: int
