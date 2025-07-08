import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from datetime import datetime

# Mock the MongoDB and MinIO dependencies
@pytest.fixture
def mock_db():
    with patch('main.files_collection') as mock_files, \
         patch('main.folders_collection') as mock_folders, \
         patch('main.users_collection') as mock_users:
        yield {
            'files': mock_files,
            'folders': mock_folders,
            'users': mock_users
        }

@pytest.fixture
def mock_minio():
    with patch('main.minio_client') as mock_client:
        yield mock_client

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

class TestFileManager:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "File Manager API is running" in response.json()["message"]

    def test_health_endpoint(self, client, mock_db, mock_minio):
        # Mock successful connections
        mock_db['files'].find_one.return_value = True
        mock_minio.bucket_exists.return_value = True
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_user_registration(self, client, mock_db):
        # Mock user doesn't exist
        mock_db['users'].find_one.return_value = None
        mock_db['users'].insert_one.return_value = MagicMock()
        
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        assert response.json()["message"] == "User registered successfully"

    def test_user_registration_duplicate_email(self, client, mock_db):
        # Mock user exists
        mock_db['users'].find_one.return_value = {"email": "test@example.com"}
        
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_file_upload_unauthorized(self, client):
        files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        response = client.post("/api/files/upload", files=files)
        assert response.status_code == 403  # Unauthorized

    def test_list_files_unauthorized(self, client):
        response = client.get("/api/files")
        assert response.status_code == 403  # Unauthorized

    def test_create_folder_unauthorized(self, client):
        folder_data = {"name": "Test Folder"}
        response = client.post("/api/folders", json=folder_data)
        assert response.status_code == 403  # Unauthorized

class TestAuthentication:
    def test_login_success(self, client, mock_db):
        from auth import get_password_hash
        
        # Mock user exists with correct password
        hashed_password = get_password_hash("password123")
        mock_db['users'].find_one.return_value = {
            "_id": "user_id",
            "email": "test@example.com",
            "hashed_password": hashed_password,
            "full_name": "Test User",
            "is_active": True
        }
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, mock_db):
        # Mock user doesn't exist
        mock_db['users'].find_one.return_value = None
        
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

class TestFileOperations:
    def get_auth_token(self, client, mock_db):
        """Helper to get authentication token"""
        from auth import get_password_hash
        
        hashed_password = get_password_hash("password123")
        mock_db['users'].find_one.return_value = {
            "_id": "user_id",
            "email": "test@example.com",
            "hashed_password": hashed_password,
            "full_name": "Test User",
            "is_active": True
        }
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        return response.json()["access_token"]

    def test_file_upload_authorized(self, client, mock_db, mock_minio):
        token = self.get_auth_token(client, mock_db)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock successful upload
        mock_minio.put_object.return_value = None
        mock_db['files'].insert_one.return_value = MagicMock()
        
        files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
        response = client.post("/api/files/upload", files=files, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "File uploaded successfully"

    def test_list_files_authorized(self, client, mock_db, mock_minio):
        token = self.get_auth_token(client, mock_db)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock file list
        mock_db['files'].find.return_value = []
        mock_db['folders'].find.return_value = []
        
        response = client.get("/api/files", headers=headers)
        assert response.status_code == 200
        assert "items" in response.json()

class TestFolderOperations:
    def get_auth_token(self, client, mock_db):
        """Helper to get authentication token"""
        from auth import get_password_hash
        
        hashed_password = get_password_hash("password123")
        mock_db['users'].find_one.return_value = {
            "_id": "user_id",
            "email": "test@example.com",
            "hashed_password": hashed_password,
            "full_name": "Test User",
            "is_active": True
        }
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        return response.json()["access_token"]

    def test_create_folder_authorized(self, client, mock_db):
        token = self.get_auth_token(client, mock_db)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock successful folder creation
        mock_db['folders'].insert_one.return_value = MagicMock()
        
        folder_data = {"name": "Test Folder"}
        response = client.post("/api/folders", json=folder_data, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Folder created successfully"

    def test_delete_non_empty_folder(self, client, mock_db):
        token = self.get_auth_token(client, mock_db)
        headers = {"Authorization": f"Bearer {token}"}
        
    def test_delete_non_empty_folder(self, client, mock_db):
        token = self.get_auth_token(client, mock_db)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock folder contains files
        mock_db['files'].count_documents.return_value = 1  # Folder has files
        mock_db['folders'].count_documents.return_value = 0
        
        response = client.delete("/api/folders/folder_id", headers=headers)
        assert response.status_code == 400
        assert "Cannot delete non-empty folder" in response.json()["detail"]

    def test_delete_empty_folder(self, client, mock_db):
        token = self.get_auth_token(client, mock_db)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock empty folder
        mock_db['files'].count_documents.return_value = 0
        mock_db['folders'].count_documents.return_value = 0
        mock_db['folders'].delete_one.return_value = MagicMock(deleted_count=1)
        
        response = client.delete("/api/folders/folder_id", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Folder deleted successfully"