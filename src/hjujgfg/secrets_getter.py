import os

API_TOKEN_KEY = "MONEY_BOT_API_KEY"


def get_api_token():
    return os.getenv(API_TOKEN_KEY)

