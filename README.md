# File Manager

A full-stack web application that allows users to manage files (upload, download, edit, delete, and list) through a web interface. Built with technologies including SvelteKit, FastAPI, MongoDB, and MinIO.

## Features

- Drag-and-drop and file selection support
- View, rename, delete, and download files
- Create and organize files in folders
- Display file name, size, upload date, and type
- Works on desktop and mobile devices
- Upload progress and error handling
- Multi-user support with login/registration
- Full-text search across file names

### Specs

- RESTful API with FastAPI
- Object storage with MinIO
- NoSQL database with MongoDB
- Frontend with SvelteKit and TailwindCSS
- Containerized deployment with Docker

### Technology Stack

- SvelteKit and TailwindCSS, 
- FastAPI, 
- MongoDB (DB),
- MinIO (Storage), 
- Docker (containerization)

## Project Structure

```
project/
├── data/                    # MongoDB and MinIO data
├── frontend/               # SvelteKit application
│   ├── src/
│   │   ├── components/     # Svelte components
│   │   ├── routes/         # SvelteKit routes
│   │   └── stores/         # Svelte stores
│   ├── node_modules/         # packages
│   ├── static/               # Icons
│   ├── postcss.config.js
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
|   ├── Dockerfile
│   └── package.json
├── backend/                # FastAPI application
│   ├── main.py            # FastAPI main application
│   ├── auth.py            # Auth functions
│   ├── config.py            # All config and settings
│   ├── models.py            # metadata model configs
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml      # Service across both Dockerfiles
├── .env     # Environment variables
└── README.md
```

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/BereketRetta/FileManage.git
   cd file-manager
   ```

2. **Create data directories**
   ```bash
   mkdir -p data/mongodb data/minio
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### API Documentation
FastAPI automatically generates interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Config

### Environment Variables

The application uses the following environment variables:

#### Backend
- `MONGODB_URL`: MongoDB connection string (default: `mongodb://mongodb:27017/filemanager`)
- `MINIO_ENDPOINT`: MinIO endpoint (default: `minio:9000`)
- `MINIO_ACCESS_KEY`: MinIO access key (default: `minioadmin`)
- `MINIO_SECRET_KEY`: MinIO secret key (default: `minioadmin`)
- `MINIO_BUCKET_NAME`: MinIO bucket name (default: `files`)

#### Frontend
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

### Logs
View logs for specific services:
```bash
docker-compose logs frontend
docker-compose logs backend
docker-compose logs mongodb
docker-compose logs minio
```

### Reset Data
To reset all data:
```bash
docker-compose down -v
rm -rf data/
mkdir -p data/mongodb data/minio
docker-compose up --build
```

