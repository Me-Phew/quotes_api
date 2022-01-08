import random
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from pydantic import Required
from sqlalchemy.orm import Session

from fastapi_limiter.depends import RateLimiter
from .. import models
from ..api_key import authorize_client
from ..config import settings
from ..database import get_db
from ..schemas.quote import CreateQuote, CreateQuotes, Language, ReturnQuote, ReturnQuotes
from ..schemas.sort import SortBy
from ..utils import convert_order_by, increase_times_accessed, rename_times_accessed
from sqlalchemy_utils import escape_like
from sqlalchemy.sql.expression import func

router = APIRouter(prefix=settings.BASE_URL + '/quotes',
                   tags=['Quotes'])


@router.get('/random', response_model=ReturnQuote, dependencies=[Depends(authorize_client),
                                                                 Depends(RateLimiter(times=10,
                                                                                     seconds=1)),
                                                                 Depends(RateLimiter(times=5_000,
                                                                                     hours=1)),
                                                                 Depends(RateLimiter(times=20_000,
                                                                                     hours=24))])
def get_random_quote(db: Session = Depends(get_db)):
    min_id = db.query(models.Quote).order_by(models.Quote.id).first().id
    max_id = db.query(models.Quote).order_by(models.Quote.id.desc()).first().id

    quote_id = random.randint(min_id, max_id)

    quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()

    quote.times_accessed += 1
    db.commit()
    db.refresh(quote)
    quote.popularity = quote.times_accessed

    return quote


@router.get('', response_model=ReturnQuotes, dependencies=[Depends(authorize_client),
                                                           Depends(RateLimiter(times=8,
                                                                               seconds=1)),
                                                           Depends(RateLimiter(times=2_000,
                                                                               hours=1)),
                                                           Depends(RateLimiter(times=8_000,
                                                                               hours=24))])
def get_quotes(db: Session = Depends(get_db),
               limit: Optional[int] = Query(100, gt=0, lt=100_000),
               offset: Optional[int] = Query(0, gt=-1, lt=10_000_000),
               order_by: Optional[SortBy] = Query(SortBy.ID),
               descending: bool = Query(False)):
    if limit and not offset:
        db_order_by = convert_order_by(order_by)

        if descending:
            quotes = db.query(models.Quote).order_by(db_order_by.desc()).limit(limit).all()
        else:
            quotes = db.query(models.Quote).order_by(db_order_by).limit(limit).all()

    elif offset and not limit:
        db_order_by = convert_order_by(order_by)

        if descending:
            quotes = db.query(models.Quote).order_by(db_order_by.desc()).offset(offset).all()
        else:
            quotes = db.query(models.Quote).order_by(db_order_by).offset(offset).all()

    elif limit and offset:
        db_order_by = convert_order_by(order_by)

        if descending:
            quotes = db.query(models.Quote).order_by(db_order_by.desc()).offset(offset).limit(limit).all()
        else:
            quotes = db.query(models.Quote).order_by(db_order_by).offset(offset).limit(limit).all()

    else:
        db_order_by = convert_order_by(order_by)

        if descending:
            quotes = db.query(models.Quote).order_by(db_order_by.desc()).all()
        else:
            quotes = db.query(models.Quote).order_by(db_order_by).all()

    quotes = list(map(increase_times_accessed, quotes))
    db.commit()
    map(db.refresh, quotes)
    quotes = list(map(rename_times_accessed, quotes))

    return {'quotes': quotes,
            'count': len(quotes)}


@router.get('/search', response_model=ReturnQuotes, dependencies=[Depends(authorize_client),
                                                                  Depends(RateLimiter(times=5,
                                                                                      seconds=1)),
                                                                  Depends(RateLimiter(times=1_000,
                                                                                      hours=1)),
                                                                  Depends(RateLimiter(times=5_000,
                                                                                      hours=24))])
def search_quotes(db: Session = Depends(get_db),
                  author_contains_ci: str = Query(None),
                  author_contains_cs: str = Query(None),
                  author_equal_ci: str = Query(None),
                  author_equal_cs: str = Query(None),
                  includes_keywords_ci: List[str] = Query(None),
                  includes_keywords_cs: List[str] = Query(None),
                  language: Optional[Language] = Query(None),
                  min_length: int = Query(None, gt=0),
                  max_length: int = Query(None, gt=0),
                  limit: Optional[int] = Query(100, gt=0, lt=100_000),
                  offset: Optional[int] = Query(0, gt=-1, lt=10_000_000),
                  order_by: Optional[SortBy] = Query(SortBy.ID),
                  descending: bool = Query(False)):
    quotes = None

    if author_contains_ci:
        if author_contains_cs or author_equal_ci or author_equal_cs:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        quotes = db.query(models.Quote).filter(models.Quote.author.ilike(f'%{escape_like(author_contains_ci)}%'))

    elif author_contains_cs:
        if author_equal_ci or author_equal_cs:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        quotes = db.query(models.Quote).filter(models.Quote.author.like(f'%{escape_like(author_contains_cs)}%'))

    elif author_equal_ci:
        if author_equal_cs:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        quotes = db.query(models.Quote).filter(func.lower(models.Quote.author) == func.lower(author_equal_ci))

    elif author_equal_cs:

        quotes = db.query(models.Quote).filter(models.Quote.author == author_equal_cs)

    if includes_keywords_ci:
        if includes_keywords_cs:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        keywords_ci = ' '.join(includes_keywords_ci)

        quotes = db.query(models.Quote).filter(models.Quote.content.ilike(f'%{escape_like(keywords_ci)}%'))
    elif includes_keywords_cs:
        keywords_cs = ' '.join(includes_keywords_cs)

        quotes = db.query(models.Quote).filter(models.Quote.content.like(f'%{escape_like(keywords_cs)}%'))

    if not quotes:
        quotes = db.query(models.Quote)

    if language:
        quotes = quotes.filter(models.Quote.language == language.value)

    if min_length:
        quotes = quotes.filter(func.length(models.Quote.content) > min_length)

    if max_length:
        if max_length < min_length:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        quotes = quotes.filter(func.length(models.Quote.content) < max_length)

    if order_by:
        db_order_by = convert_order_by(order_by)

        if descending:
            quotes = quotes.order_by(db_order_by.desc())
        else:
            quotes = quotes.order_by(db_order_by)

    if limit:
        quotes = quotes.limit(limit)

    if offset:
        quotes = quotes.offset(offset)

    print(quotes)
    quotes = quotes.all()

    quotes = list(map(increase_times_accessed, quotes))
    db.commit()
    map(db.refresh, quotes)
    quotes = list(map(rename_times_accessed, quotes))

    return {'quotes': quotes,
            'count': len(quotes)}


@router.get('/{quote_id}', response_model=ReturnQuote, dependencies=[Depends(authorize_client),
                                                                     Depends(RateLimiter(times=10,
                                                                                         seconds=1)),
                                                                     Depends(RateLimiter(times=5_000,
                                                                                         hours=1)),
                                                                     Depends(RateLimiter(times=20_000,
                                                                                         hours=24))])
def get_quote_by_id(db: Session = Depends(get_db),
                    quote_id: int = Path(Required)):
    quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()

    quote.times_accessed += 1
    db.commit()
    db.refresh(quote)
    quote.popularity = quote.times_accessed

    return quote


@router.post('/add_one', response_model=ReturnQuote, dependencies=[Depends(authorize_client),
                                                                   Depends(RateLimiter(times=8,
                                                                                       seconds=1)),
                                                                   Depends(RateLimiter(times=2_000,
                                                                                       hours=1)),
                                                                   Depends(RateLimiter(times=10_000,
                                                                                       hours=24))])
def add_quote(quote: CreateQuote,
              db: Session = Depends(get_db)):
    db_quote = models.Quote(**quote.dict())

    db.add(db_quote)

    db.commit()

    db.refresh(db_quote)

    return db_quote


@router.post('/add_batch', response_model=ReturnQuotes, dependencies=[Depends(authorize_client),
                                                                      Depends(RateLimiter(times=9,
                                                                                          seconds=1)),
                                                                      Depends(RateLimiter(times=4_000,
                                                                                          hours=1)),
                                                                      Depends(RateLimiter(times=10_000,
                                                                                          hours=24))])
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
