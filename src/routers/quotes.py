import random
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from pydantic import Required
from sqlalchemy.orm import Session

from .. import models
from ..api_key import authorize_client
from ..config import settings
from ..database import get_db
from ..schemas.quote import CreateQuote, CreateQuotes, Language, ReturnQuote, ReturnQuotes
from ..schemas.sort import SortBy
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix=settings.BASE_URL + '/quotes',
                   tags=['Quotes'])


@router.get('/random', response_model=ReturnQuote, dependencies=[Depends(authorize_client),
                                                                 Depends(RateLimiter(times=10,
                                                                                     seconds=1))])
def get_random_quote(db: Session = Depends(get_db)):
    quote_id = random.randint(1, 1000)

    quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()

    return quote


@router.get('', response_model=ReturnQuotes, dependencies=[Depends(authorize_client)])
def get_quotes(db: Session = Depends(get_db),
               limit: Optional[int] = Query(100, gt=0, lt=100_000),
               offset: Optional[int] = Query(0, gt=-1, lt=10_000_000),
               sort_by: Optional[SortBy] = SortBy.ID,
               descending: bool = False):

    if limit and not offset:
        quotes = db.query(models.Quote).limit(limit).all()

    elif offset and not limit:
        quotes = db.query(models.Quote).offset(offset).all()

    elif limit and offset:
        quotes = db.query(models.Quote).offset(offset).limit(limit).all()

    else:
        quotes = db.query(models.Quote).all()

    return {'quotes': quotes,
            'count': len(quotes)}


@router.get('/search', dependencies=[Depends(authorize_client)], description='asdas/*')
def search_quotes(db: Session = Depends(get_db),
                  author: str = Query(None),
                  includes_keywords: List[str] = Query(None),
                  language: Optional[Language] = Query(None),
                  min_length: int = Query(None, gt=0),
                  max_length: int = Query(None, gt=0),
                  limit: Optional[int] = Query(100, gt=0, lt=100_000),
                  offset: Optional[int] = Query(0, gt=-1, lt=10_000_000)):
    print(language)


@router.get('/{id}', response_model=ReturnQuote, dependencies=[Depends(authorize_client)])
def get_quote_by_id(db: Session = Depends(get_db),
                    quote_id: int = Path(Required)):
    quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()

    return quote


@router.post('/add_one', response_model=ReturnQuote, dependencies=[Depends(authorize_client)])
def add_quote(quote: CreateQuote,
              db: Session = Depends(get_db)):
    db_quote = models.Quote(**quote.dict())

    db.add(db_quote)

    db.commit()

    db.refresh(db_quote)

    return db_quote


@router.post('/add_batch', response_model=ReturnQuotes, dependencies=[Depends(authorize_client)])
def add_quotes(quotes: CreateQuotes,
               db: Session = Depends(get_db)):
    quotes = quotes.dict().get('quotes')

    def create_db_quote(quote):
        return models.Quote(**quote)

    db_quotes = list(map(create_db_quote, quotes))
    map(db.add, db_quotes)

    db.commit()

    map(db.refresh, db_quotes)

    return {'quotes': db_quotes,
            'count': len(db_quotes)}
