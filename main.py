from operator import methodcaller
from src.database import get_db
from src import models


def get_quotes(file_path):
    def stripe_nums(item):
        text = item[0]
        text = text[text.find('.') + 2:]
        return [text, item[1]]

    db = next(get_db())

    with open(file_path, 'r', encoding='utf-8') as quotes_file:
        quotes = quotes_file.read()
        quotes = quotes.split('\n')
        quotes = list(filter(''.__ne__, quotes))
        quotes = list(map(methodcaller("split", " – "), quotes))
        quotes = list(map(stripe_nums, quotes))
        for quote in quotes:
            db_quote = {
                'content': quote[0],
                'author': quote[1],
                'language': 'en'
            }

            db_quote = models.Quote(**db_quote)

            db.add(db_quote)
        db.commit()


def main():
    get_quotes('cytaty.txt')


if __name__ == "__main__":
    main()
