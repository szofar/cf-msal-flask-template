"""Contains all settings for the app"""

from os import getenv


class Settings:

    # database
    DB_NAME = getenv("DB_NAME", "")
    DB_CONNECTION_STRING = getenv("DB_CONNECTION_STRING", "")

    # MSAL
    AUTHORITY = getenv("AUTHORITY", "")
    CLIENT_ID = getenv("CLIENT_ID", "")  # application (client) ID from app registration
    CLIENT_SECRET = getenv("CLIENT_SECRET", "")
    REDIRECT_PATH = "/auth"  # used when forming an absolute URL for your redirect URI
    SCOPE = []
    SESSION_COOKIE_NAME = "JSESSIONID"
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"  # the token cache is stored in server-side session
    SECRET_KEY = getenv("SECRET_KEY", "")
