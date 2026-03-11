import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "infymart-secret-key")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "project")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_AUTOCOMMIT = os.getenv("MYSQL_AUTOCOMMIT", "True").lower() == "true"