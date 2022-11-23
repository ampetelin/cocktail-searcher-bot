from httpx import TransportError

COCKTAIL_RESPONSE = {
    "count": 3,
    "total_pages": 3,
    "next": "https://api.example.org/accounts/?page=3",
    "previous": "https://api.example.org/accounts/?page=1",
    "results": [
        {
            "id": 1,
            "name": "string",
            "image_url": "https://example.com/cocktail_image.jpg",
            "categories": [
                {
                    "id": 1,
                    "name": "string"
                }
            ],
            "composition": [
                {
                    "ingredient_name": "string",
                    "amount": 32767,
                    "unit_name": "string"
                }
            ]
        }
    ]
}

PAGINATION_EMPTY_RESPONSE_RESULT = {
    "count": 0,
    "total_pages": 1,
    "next": None,
    "previous": None,
    "results": []
}

COCKTAIL_RECIPE_RESPONSE = [
    {
        "stage": 1,
        "action": "string"
    },
    {
        "stage": 2,
        "action": "string"
    }
]

TELEGRAM_USER_RESPONSE = {
    "count": 3,
    "total_pages": 3,
    "next": "http://api.example.org/accounts/?page=3",
    "previous": "http://api.example.org/accounts/?page=1",
    "results": [
        {
            "id": 1,
            "chat_id": 12345
        }
    ]
}

CREATE_TELEGRAM_USER_RESPONSE = {
    "id": 1,
    "chat_id": 12345
}

CREATE_TELEGRAM_USER_BAD_REQUEST_RESPONSE = {
    "chat_id": ["Telegram user with this Chat ID already exists."]
}

TELEGRAM_USER_FAVORITE_RESPONSE = {
    "count": 3,
    "total_pages": 3,
    "next": "http://api.example.org/accounts/?page=3",
    "previous": "http://api.example.org/accounts/?page=1",
    "results": [
        {
            "id": 1,
            "cocktail": {
                "id": 1,
                "name": "string",
                "image_url": "https://example.com/cocktail_image.jpg",
                "categories": [
                    {
                        "id": 1,
                        "name": "string"
                    }
                ],
                "composition": [
                    {
                        "ingredient_name": "string",
                        "amount": 32767,
                        "unit_name": "string"
                    }
                ]
            },
            "created_at": "2022-11-03T09:19:03.793Z"
        }
    ]
}

ADD_COCKTAIL_TO_FAVORITES_COCKTAIL_BAD_REQUEST_RESPONSE = {
    "non_field_errors": [
        "The fields telegram_user, cocktail must make a unique set."
    ]
}

TRANSPORT_EXCEPTION = TransportError('Connection refused')
