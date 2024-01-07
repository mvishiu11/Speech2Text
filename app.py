from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import whisper
import datetime
import os
import glob
import asyncio
import queue
import uuid
import shutil

# Create FastAPI app
app = FastAPI()

# Queue for tasks
task_queue = queue.Queue(maxsize=3)

# Dictionary to store task status
tasks = {}
def dir_size_adjust(dir_path, num_files=10, size_limit = 100000000):
    """_summary_: Adjusts the number of files in the directory to 10 by deleting the oldest files.

    Args:
        file_path (str): Path to the directory.
        num_files (int, optional): Number of files to keep. Defaults to 10.
        size_limit (int, optional): Maximum size of the directory in bytes. Defaults to 100000000.
    """
    files = glob.glob(f"{dir_path}\*")
    try:
        if len(files) > num_files:
            files.sort(key=os.path.getmtime)
            for i in range(len(files) - 10):
                os.remove(files[i])
            files = glob.glob(f"{dir_path}\*")
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        if sum(os.path.getsize(f) for f in files) > size_limit:
            files.sort(key=os.path.getmtime)
            while sum(os.path.getsize(f) for f in files) > size_limit:
                os.remove(files[0])
            files = glob.glob(f"{dir_path}\*")
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        else:
            files.sort(key=os.path.getmtime, reverse=True)
            return True
    except Exception as e:
        print(e)
        return False


def translate_speech(file_path, task_id):
    """_summary_: Translates speech from an audio file to text and stores the result in the tasks dictionary.

    Args:
        file_path (str): Path to the audio file.
        task_id (str): Unique ID of the task.
    """
    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        tasks[task_id]['status'] = 'finished'
        tasks[task_id]['result'] = result['text']
        file_name = file_path.split("/")[-1].split(".")[0] + ".txt"
        print(f"Saved translation run to runs\{file_name}")
        with open(f"runs\\{file_name}", "w") as file:
            file.write(result['text'])
        dir_size_adjust("runs")
    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['result'] = str(e)# Other helper functions (dir_size_adjust, translate_speech) remain the same

async def task_processor():
    while True:
        task_id, file_path = await asyncio.to_thread(task_queue.get)
        tasks[task_id]['status'] = 'running'
        translate_speech(file_path, task_id)

# Start the task processor in an asyncio event loop
asyncio.create_task(task_processor())

@app.post("/translate")
async def translate(file: UploadFile = File(...)):
    """_summary_: Endpoint for uploading an audio file and translating it to text.

    HTTP Request Args:
        file (file): Audio file to be translated.
        
    HTTP status codes cheatsheet:
        202: Task accepted.
        400: Bad request.
        404: Task ID not found.
        429: Too many requests.
        500: Internal server error. Ergo something is wrong with this app.py file.
    
    Returns:
        JSON: JSON object containing the task ID.
        int: HTTP status code.
    """
    if task_queue.full():
        raise HTTPException(status_code=429, detail="Queue limit reached")
    
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    filename = f"upload-{timestamp}-{file.filename}"
    file_path = os.path.join("uploads/", filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    dir_size_adjust("uploads")
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending', 'result': None}
    task_queue.put((task_id, file_path))

    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def status(task_id: str):
    """_summary_: Endpoint for checking the status of a task.

    Possible task statuses:
        pending: Task has been accepted and is waiting to be processed.
        running: Task is being processed.
        finished: Task has been processed successfully.
        failed: Task failed to be processed.
    
    Args:
        task_id (str): Unique ID of the task.

    Returns:
        JSON: JSON object containing the status of the task.
        int: HTTP status code (optional, 404 if task ID is invalid)
    """
    task = tasks.get(task_id)
    if task:
        return task
    raise HTTPException(status_code=404, detail="Invalid task ID")

@app.get("/result/{task_id}")
async def result(task_id: str):
    """_summary_: Endpoint for getting the result of a task.

    Args:
        task_id (str): Unique ID of the task.

    Returns:
        JSON: JSON object containing the result of the task.
        int: HTTP status code (optional, 404 if task ID is invalid)
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Invalid task ID")
    
    if task['status'] == 'finished':
        return {"text": task['result']}
    elif task['status'] == 'failed':
        raise HTTPException(status_code=500, detail=task['result'])
    else:
        raise HTTPException(status_code=400, detail="Task has not finished yet")
