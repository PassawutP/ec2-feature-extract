import os
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from uuid import uuid4
import shutil

from app.tasks import process_urls_task

app = FastAPI()

UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = os.getcwd()
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process")
async def process_files(whitelist: UploadFile = File(...), blacklist: UploadFile = File(...)):

    whitelist_filename = os.path.join(UPLOAD_DIR, f"{uuid4()}_whitelist.txt")
    blacklist_filename = os.path.join(UPLOAD_DIR, f"{uuid4()}_blacklist.txt")
    
    with open(whitelist_filename, "wb") as f:
        shutil.copyfileobj(whitelist.file, f)
    with open(blacklist_filename, "wb") as f:
        shutil.copyfileobj(blacklist.file, f)
    
    task = process_urls_task.delay(whitelist_filename, blacklist_filename)
    
    return JSONResponse({"task_id": task.id, "message": "Task submitted successfully"})

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    csv_filename = f"PhishingLink/Features_{task_id}.csv"
    output_name = f"Features_{task_id}.csv"

    # Check if the CSV file exists
    if os.path.exists(csv_filename):
        return {"task_id": task_id, "status": "SUCCESS", "csv_path": output_name}
    
    # If the CSV file doesn't exist, check the Celery task state
    task_result = process_urls_task.AsyncResult(task_id)
    
    if task_result.state == "PENDING":
        return {"task_id": task_id, "status": "PENDING"}
    elif task_result.state != "FAILURE":
        return {"task_id": task_id, "status": task_result.state, "result": task_result.result}
    else:
        return {"task_id": task_id, "status": "FAILURE", "error": str(task_result.info)}


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")