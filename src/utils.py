from .schemas.sort import SortBy
from . import models
from .exceptions import InvalidEnumerationMemberException


def convert_order_by(order_by: SortBy):
    match order_by:
        case SortBy.ID:
            db_order_by = models.Quote.id
        case SortBy.AUTHOR:
            db_order_by = models.Quote.author
        case SortBy.LANGUAGE:
            db_order_by = models.Quote.language
        case SortBy.POPULARITY:
            db_order_by = models.Quote.times_accessed
        case SortBy.CREATED_AT:
            db_order_by = models.Quote.created_at
        case _:
            raise InvalidEnumerationMemberException

    return db_order_by


def increase_times_accessed(quote):
    quote.times_accessed += 1
    return quote


def rename_times_accessed(quote):
    quote.popularity = quote.times_accessed
    return quote


def create_db_quote(quote):
    return models.Quote(**quote)
