from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, ARRAY
from .database import Base


class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    author = Column(String, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
