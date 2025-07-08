from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ItemType(str, Enum):
    FILE = "file"
    FOLDER = "folder"

class FileMetadata(BaseModel):
    name: str
    size: int
    content_type: str
    upload_date: datetime
    file_id: str
    folder_id: Optional[str] = None
    item_type: ItemType = ItemType.FILE

class FolderMetadata(BaseModel):
    name: str
    created_date: datetime
    folder_id: str
    parent_folder_id: Optional[str] = None
    item_type: ItemType = ItemType.FOLDER

class FileUpdate(BaseModel):
    name: Optional[str] = None
    folder_id: Optional[str] = None

class FolderCreate(BaseModel):
    name: str
    parent_folder_id: Optional[str] = None

class FolderUpdate(BaseModel):
    name: str

class ItemMove(BaseModel):
    item_id: str
    item_type: ItemType
    target_folder_id: Optional[str] = None