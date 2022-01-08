from pydantic import BaseModel
from datetime import datetime
from typing import List
from enum import Enum


class Language(Enum):
    polish = "pl"
    english = "en"


class ReturnQuote(BaseModel):
    id: int
    content: str
    author: str
    language: Language
    created_at: datetime

    class Config:
        orm_mode = True


class ReturnQuotes(BaseModel):
    quotes: List[ReturnQuote]
    count: int

    class Config:
        orm_mode = True


class CreateQuote(BaseModel):
    content: str
    author: str
    language: Language

    class Config:
        orm_mode = True


class CreateQuotes(BaseModel):
    quotes: List[CreateQuote]
