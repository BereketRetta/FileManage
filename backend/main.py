from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from minio import Minio
from minio.error import S3Error
import os
import logging
from datetime import datetime, timedelta
import io
from typing import List, Optional
from config import settings
from models import (
    FileMetadata, FolderMetadata, FileUpdate, FolderCreate, 
    FolderUpdate, ItemMove, ItemType
)
from auth import (
    UserCreate, UserLogin, Token, User, get_current_user,
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# MongoDB client
try:
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    files_collection = db.files
    folders_collection = db.folders
    users_collection = db.users
    # Test connection
    client.admin.command('ping')
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# MinIO client
try:
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )
    
    # Ensure bucket exists
    if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
        minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
        logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET_NAME}")
    else:
        logger.info(f"Connected to MinIO bucket: {settings.MINIO_BUCKET_NAME}")
        
except Exception as e:
    logger.error(f"Failed to connect to MinIO: {e}")
    raise

@app.get("/")
async def root():
    return {
        "message": "File Manager API is running",
        "version": settings.VERSION,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    try:
        # Check MongoDB connection
        client.admin.command('ping')
        mongo_status = "healthy"
    except Exception:
        mongo_status = "unhealthy"
    
    try:
        # Check MinIO connection
        minio_client.bucket_exists(settings.MINIO_BUCKET_NAME)
        minio_status = "healthy"
    except Exception:
        minio_status = "unhealthy"
    
    return {
        "status": "healthy" if mongo_status == "healthy" and minio_status == "healthy" else "unhealthy",
        "mongodb": mongo_status,
        "minio": minio_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/api/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_doc = {
            "_id": ObjectId(),
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        users_collection.insert_one(user_doc)
        
        return {"message": "User registered successfully"}
        
    except Exception as e:
        if "Email already registered" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    try:
        # Find user by email
        user = users_collection.find_one({"email": user_credentials.email})
        if not user or not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        if "Incorrect email or password" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# File management endpoints
@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...), 
    folder_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    try:
        # Debug logging
        logger.info(f"Upload request - File: {file.filename}, Folder ID: {folder_id}, User: {current_user.id}")
        
        # Generate unique file ID
        file_id = str(ObjectId())
        
        # Read file content
        content = await file.read()
        
        # Upload to MinIO
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            file_id,
            io.BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        
        # Save metadata to MongoDB
        file_metadata = {
            "_id": ObjectId(file_id),
            "name": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "upload_date": datetime.utcnow(),
            "file_id": file_id,
            "folder_id": folder_id,  # This should properly store the folder_id
            "item_type": "file",
            "user_id": current_user.id
        }
        
        # Debug logging
        logger.info(f"Saving file metadata: {file_metadata}")
        
        files_collection.insert_one(file_metadata)
        
        return {
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "folder_id": folder_id
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/files")
async def list_files(
    folder_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    try:
        # Build base query to include user_id filter
        base_query = {"user_id": current_user.id}
        
        # If search query is provided, search across all folders
        if search and search.strip():
            search_term = search.strip()
            logger.info(f"Searching for: {search_term}")
            
            items = []
            
            # Search all folders for the user (case-insensitive)
            folder_search_query = {
                **base_query,
                "name": {"$regex": search_term, "$options": "i"}
            }
            
            for folder_doc in folders_collection.find(folder_search_query):
                items.append({
                    "id": str(folder_doc["_id"]),
                    "name": folder_doc["name"],
                    "created_date": folder_doc["created_date"].isoformat(),
                    "folder_id": folder_doc["folder_id"],
                    "parent_folder_id": folder_doc.get("parent_folder_id"),
                    "item_type": "folder"
                })
            
            # Search all files for the user (case-insensitive)
            file_search_query = {
                **base_query,
                "name": {"$regex": search_term, "$options": "i"}
            }
            
            for file_doc in files_collection.find(file_search_query):
                items.append({
                    "id": str(file_doc["_id"]),
                    "name": file_doc["name"],
                    "size": file_doc["size"],
                    "content_type": file_doc["content_type"],
                    "upload_date": file_doc["upload_date"].isoformat(),
                    "file_id": file_doc["file_id"],
                    "folder_id": file_doc.get("folder_id"),
                    "item_type": "file"
                })
            
            logger.info(f"Search found {len(items)} items")
            return {"items": items, "current_folder": folder_id, "search_term": search_term}
        
        # Regular folder browsing (no search)
        if folder_id:
            file_query = {**base_query, "folder_id": folder_id}
            folder_query = {**base_query, "parent_folder_id": folder_id}
        else:
            file_query = {**base_query, "folder_id": {"$in": [None, ""]}}
            folder_query = {**base_query, "parent_folder_id": {"$in": [None, ""]}}
        
        items = []
        
        # Get folders in current directory
        for folder_doc in folders_collection.find(folder_query):
            items.append({
                "id": str(folder_doc["_id"]),
                "name": folder_doc["name"],
                "created_date": folder_doc["created_date"].isoformat(),
                "folder_id": folder_doc["folder_id"],
                "parent_folder_id": folder_doc.get("parent_folder_id"),
                "item_type": "folder"
            })
        
        # Get files in current directory
        for file_doc in files_collection.find(file_query):
            items.append({
                "id": str(file_doc["_id"]),
                "name": file_doc["name"],
                "size": file_doc["size"],
                "content_type": file_doc["content_type"],
                "upload_date": file_doc["upload_date"].isoformat(),
                "file_id": file_doc["file_id"],
                "folder_id": file_doc.get("folder_id"),
                "item_type": "file"
            })
            
        return {"items": items, "current_folder": folder_id}
    except Exception as e:
        logger.error(f"Error in list_files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list items: {str(e)}")

@app.get("/api/files/{file_id}/download")
async def download_file(
    file_id: str, 
    current_user: User = Depends(get_current_user)
):
    try:
        # Get file metadata from MongoDB and verify ownership
        file_doc = files_collection.find_one({
            "file_id": file_id, 
            "user_id": current_user.id
        })
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file from MinIO
        response = minio_client.get_object(settings.MINIO_BUCKET_NAME, file_id)
        
        def iterfile():
            try:
                for chunk in response:
                    yield chunk
            finally:
                response.close()
                response.release_conn()
        
        return StreamingResponse(
            iterfile(),
            media_type=file_doc["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename={file_doc['name']}"
            }
        )
        
    except S3Error as e:
        raise HTTPException(status_code=404, detail="File not found in storage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.put("/api/files/{file_id}")
async def update_file(
    file_id: str, 
    file_update: FileUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        # Update file metadata in MongoDB with user verification
        result = files_collection.update_one(
            {"file_id": file_id, "user_id": current_user.id},
            {"$set": {"name": file_update.name}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"message": "File updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.delete("/api/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        # Delete file metadata from MongoDB with user verification
        result = files_collection.delete_one({
            "file_id": file_id, 
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file from MinIO
        try:
            minio_client.remove_object(settings.MINIO_BUCKET_NAME, file_id)
        except S3Error:
            # File might not exist in MinIO, but we've already deleted from MongoDB
            pass
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# Folder management endpoints
@app.post("/api/folders")
async def create_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        folder_id = str(ObjectId())
        
        folder_metadata = {
            "_id": ObjectId(folder_id),
            "name": folder_data.name,
            "created_date": datetime.utcnow(),
            "folder_id": folder_id,
            "parent_folder_id": folder_data.parent_folder_id,
            "item_type": "folder",
            "user_id": current_user.id  # Associate with user
        }
        
        folders_collection.insert_one(folder_metadata)
        
        return {
            "message": "Folder created successfully",
            "folder_id": folder_id,
            "name": folder_data.name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")

@app.put("/api/folders/{folder_id}")
async def update_folder(
    folder_id: str, 
    folder_update: FolderUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = folders_collection.update_one(
            {"folder_id": folder_id, "user_id": current_user.id},
            {"$set": {"name": folder_update.name}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        return {"message": "Folder updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@app.delete("/api/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        # Check if folder contains any items (with user verification)
        files_count = files_collection.count_documents({
            "folder_id": folder_id, 
            "user_id": current_user.id
        })
        subfolders_count = folders_collection.count_documents({
            "parent_folder_id": folder_id, 
            "user_id": current_user.id
        })
        
        if files_count > 0 or subfolders_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete non-empty folder")
        
        result = folders_collection.delete_one({
            "folder_id": folder_id, 
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        return {"message": "Folder deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.get("/api/folders/{folder_id}/breadcrumb")
async def get_folder_breadcrumb(
    folder_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        breadcrumb = []
        current_folder_id = folder_id
        
        while current_folder_id:
            folder = folders_collection.find_one({
                "folder_id": current_folder_id, 
                "user_id": current_user.id
            })
            if not folder:
                break
                
            breadcrumb.insert(0, {
                "folder_id": folder["folder_id"],
                "name": folder["name"]
            })
            current_folder_id = folder.get("parent_folder_id")
        
        # Add root folder
        breadcrumb.insert(0, {"folder_id": None, "name": "Home"})
        
        return {"breadcrumb": breadcrumb}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get breadcrumb: {str(e)}")
