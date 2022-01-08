from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    author = Column(String, nullable=False)
    language = Column(String, nullable=False)
    times_accessed = Column(Integer, nullable=False, server_default=text('0'))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
