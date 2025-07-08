import os
from typing import Optional


class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL", "mongodb://localhost:27017/filemanager")
    MONGODB_DB_NAME: str = "filemanager"

    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "files")
    MINIO_SECURE: bool = False

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "File Manager API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for file management"

    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt',
        'zip', 'rar', 'gz',
        'mp4', 'mov', 'webm', 'mkv', 'mp3', 'wav',
        'py', 'js', 'html', 'md'
    }

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://frontend:3000",
    ]


settings = Settings()
