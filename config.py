import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Supabase/Railway typically provide postgres:// URLs.
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH"))

    OCR_PROVIDER = os.getenv("OCR_PROVIDER", "paddle")
    OCR_ENABLE_FALLBACK = os.getenv("OCR_ENABLE_FALLBACK", "true").lower() == "true"
    OCR_PDF_MAX_PAGES = int(os.getenv("OCR_PDF_MAX_PAGES", "10"))

    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")