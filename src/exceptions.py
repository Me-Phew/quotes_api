from fastapi import HTTPException, status


class InvalidApiKeyException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate credentials"
        self.headers = {"WWW-Authenticate": "x-api_key"}


class InvalidEnumerationMemberException(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.detail = {
            "detail": [
                {
                    "loc": [
                        "query",
                        "order_by"
                    ],
                    "msg": "value is not a valid enumeration member; permitted: 'id', 'author', 'language', "
                           "'popularity', 'created_at'",
                    "type": "type_error.enum",
                    "ctx": {
                        "enum_values": [
                            "id",
                            "author",
                            "language",
                            "popularity",
                            "created_at"
                        ]
                    }
                }
            ]
        }
