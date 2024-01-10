from fastapi import FastAPI, UploadFile, File, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import whisper
import datetime
import os
import glob
import asyncio
import queue
import uuid
import shutil
from typing import List
import warnings
import logging
import soundfile as sf
import io
import tempfile

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Save the original warning handler
original_showwarning = warnings.showwarning

# Custom warning handler to suppress the warning about FP16 not being supported on CPU
def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    whisper_message = "FP16 is not supported on CPU; using FP32 instead"
    if issubclass(category, UserWarning) and whisper_message in str(message):
        logger.warning("Running on CPU. FP16 not supported, using FP32 instead.")
    else:
        warnings.showwarning = original_showwarning
        warnings.showwarning(message, category, filename, lineno, file, line)

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
    files = glob.glob(os.path.join(dir_path, "*"))
    try:
        if len(files) > num_files:
            files.sort(key=os.path.getmtime)
            for i in range(len(files) - 10):
                os.remove(files[i])
            files = glob.glob(os.path.join(dir_path, "*"))
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        if sum(os.path.getsize(f) for f in files) > size_limit:
            files.sort(key=os.path.getmtime)
            while sum(os.path.getsize(f) for f in files) > size_limit:
                os.remove(files[0])
                logger.info(f"Removed file {files[0]}")
                files = glob.glob(os.path.join(dir_path, "*"))
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        else:
            files.sort(key=os.path.getmtime, reverse=True)
            return True
    except FileNotFoundError:
        logger.error(f"Directory not found: {dir_path}", exc_info=True)
    except PermissionError:
        logger.error(f"Permission denied for directory: {dir_path}", exc_info=True)
    except Exception as e:
        logger.error("An unexpected error occurred in dir_size_adjust", exc_info=True)
    return False

def dict_size_adjust(dict, num_items=10):
    """_summary_: Adjusts the number of items in the dictionary to 10 by deleting the oldest items.

    Args:
        dict (dict): Dictionary to be adjusted.
        num_items (int, optional): Number of items to keep. Defaults to 10.
    """
    try:
        keys = list(dict.keys())
        keys.sort(key=lambda x: dict[x]['timestamp'])
        if len(dict) > num_items:
            for i in range(len(dict) - num_items):
                logger.info(f"Removed task {keys[i]}")
                del dict[keys[i]]
            return True
        else:
            return True
    except Exception as e:
        logger.error(f"An unexpected error occurred in dict_size_adjust: {e}", exc_info=True)
        return False

def translate_speech(file_path, task_id):
    """_summary_: Translates speech from an audio file to text and stores the result in the tasks dictionary.

    Args:
        file_path (str): Path to the audio file.
        task_id (str): Unique ID of the task.
    """
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.showwarning = custom_warning_handler
            model = whisper.load_model("base")
            result = model.transcribe(file_path)
            warnings.showwarning = original_showwarning
        tasks[task_id]['status'] = 'finished'
        tasks[task_id]['result'] = result['text']
        file_name = os.path.normpath(file_path).split(os.sep)[-1].split(".")[0] + ".txt"
        save_path = os.path.join("runs", file_name)
        with open(save_path, "w") as file:
            file.write(result['text'])
        logger.info(f"Saved translation run to {save_path}")
        dir_size_adjust("runs")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}", exc_info=True)
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['result'] = 'File not found'
    except IOError as e:
        logger.error(f"IO error: {e}", exc_info=True)
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['result'] = f'IO error occurred: {e}'
    except Exception as e:
        logger.error("An unexpected error occurred", exc_info=True)
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['result'] = f'An unexpected error occurred: {e}'

async def task_processor():
    while True:
        try:
            task_id, file_path = await asyncio.to_thread(task_queue.get)
            tasks[task_id]['status'] = 'running'
            translate_speech(file_path, task_id)
        except Exception as e:
            logger.error("Error in task processing", exc_info=True)
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['result'] = str(e)

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
        JSON: JSON object containing the task ID and the status code.
    """
    if task_queue.full():
        raise HTTPException(status_code=429, detail="Queue limit reached")
    
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    filename = f"upload-{timestamp}-{file.filename}"
    file_path = os.path.join("uploads", filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        buffer.flush()
        os.fsync(buffer.fileno())
        
    logger.info(f"Saved uploaded file to {file_path}")
    dir_size_adjust("uploads")
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'timestamp': datetime.datetime.now().timestamp(), 'status': 'pending', 'result': None}
    
    await asyncio.to_thread(task_queue.put, (task_id, file_path))
    size_adjusted = dict_size_adjust(tasks)
    if not size_adjusted:
        logger.error("Failed to adjust tasks dictionary size", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error, failed to adjust tasks dictionary size")

    return JSONResponse(content={"task_id": task_id}, status_code=202)

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
    """
    task = tasks.get(task_id)
    if task:
        return JSONResponse(content={"status": task['status']})
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
        return JSONResponse(content={"text": task['result']}, status_code=200)
    elif task['status'] == 'failed':
        return JSONResponse(content={"error": task['result']}, status_code=400)
    else:
        raise HTTPException(status_code=400, detail="Task has not finished yet")
    
    
@app.get("/tasks")
async def get_tasks(fields: List[str] = Query(None, description="List of fields to be returned", example=["status", "result"])
                  , limit: int = Query(10, description="Maximum number of tasks to be returned", example=10)
                  , size: int = Query(0, description="Whether to return the size of the tasks dictionary", example=0)):
    """_summary_: Endpoint for getting all tasks. Logs requests to the server console.

    Returns:
        JSON: JSON object containing all tasks.
    """
    if size==1:
        return {"size": len(tasks)}
    if fields:
        output = {}
        for i in range(limit):
            try:
                output[list(tasks.keys())[i]] = {field: tasks[list(tasks.keys())[i]][field] for field in fields}
            except IndexError:
                break
        return JSONResponse(content=output)
    else:
        output = {}
        for i in range(limit):
            try:
                output[list(tasks.keys())[i]] = tasks[list(tasks.keys())[i]]
            except IndexError:
                break
        return JSONResponse(content=output)
    
    
@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket, required_chunk_size_in_bytes: int = 16000):
    await websocket.accept()
    buffer = io.BytesIO()
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'timestamp': datetime.datetime.now().timestamp(), 'status': 'pending', 'result': None}

    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            buffer.write(audio_chunk)

            # Check if buffer has enough data to process (e.g., 5 seconds of audio)
            if buffer.tell() >= required_chunk_size_in_bytes:
                buffer.seek(0)
                # Process the audio chunk
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    # Assuming the audio is in WAV format
                    sf.write(temp_file, buffer.getvalue(), samplerate=16000)
                    translate_speech(temp_file.name, task_id)
                    tasks[task_id]['status'] = 'running'
                    buffer.seek(0)
                    buffer.truncate()
                
                # Send the result back
                await websocket.send_json({"task_id": task_id, "result": tasks[task_id]['result']})

    except WebSocketDisconnect:
        print(f"WebSocket disconnected, task_id: {task_id}")
        # Handle cleanup here

    finally:
        buffer.close()