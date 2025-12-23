
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "local_storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.put("/upload/{filename:path}")
async def upload_file(filename: str, request: Request):
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write incoming binary stream to file
    try:
        with open(file_path, "wb") as f:
            async for chunk in request.stream():
                f.write(chunk)
        return {"status": "ok", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{filename:path}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
