from flask import Flask, request, jsonify
from regex import P
import whisper
import datetime
import os
import glob
import threading
import queue
import uuid

app = Flask(__name__)

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
    files = glob.glob(f"{dir_path}*")
    try:
        if len(files) > num_files:
            files.sort(key=os.path.getmtime)
            for i in range(len(files) - 10):
                os.remove(files[i])
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        if sum(os.path.getsize(f) for f in files) > size_limit:
            files.sort(key=os.path.getmtime)
            while sum(os.path.getsize(f) for f in files) > size_limit:
                os.remove(files[0])
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
        tasks[task_id]['result'] = str(e)

def task_processor():
    """_summary_: Processes tasks from the task queue."""
    while True:
        task_id, file_path = task_queue.get()
        tasks[task_id]['status'] = 'running'
        translate_speech(file_path, task_id)

# Start the task processor in a separate thread
thread = threading.Thread(target=task_processor, daemon=True)
thread.start()

@app.route('/translate', methods=['POST'])
def translate():
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
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    if task_queue.full():
        return jsonify({"error": "Queue limit reached"}), 429
    
    print(f"Received request from {request.remote_addr} with {request.files['file'].filename} file.")

    file = request.files['file']
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"upload-{timestamp}{file_extension}"
    file_path = os.path.join("uploads/", filename)
    file.save(file_path)
    dir_size_adjust("uploads")
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending', 'result': None}
    task_queue.put((task_id, file_path))

    return jsonify({"task_id": task_id}), 202

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
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
    if task_id in tasks:
        return jsonify(tasks[task_id])
    else:
        return jsonify({"error": "Invalid task ID"}), 404
    
@app.route('/result/<task_id>', methods=['GET'])
def result(task_id):
    """_summary_: Endpoint for getting the result of a task.

    Args:
        task_id (str): Unique ID of the task.

    Returns:
        JSON: JSON object containing the result of the task.
        int: HTTP status code (optional, 404 if task ID is invalid)
    """
    if task_id in tasks:
        if tasks[task_id]['status'] == 'finished':
            return jsonify({"text": tasks[task_id]['result']})
        elif tasks[task_id]['status'] == 'failed':
            return jsonify({"error": tasks[task_id]['result']}), 500
        else:
            return jsonify({"error": "Task has not finished yet"}), 400
    else:
        return jsonify({"error": "Invalid task ID"}), 404

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("runs"):
        os.makedirs("runs")    
    app.run(debug=True) # Remove debug=True when deploying to production