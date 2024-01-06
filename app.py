from flask import Flask, request, jsonify
import whisper
import datetime
import os
import threading
import queue
import uuid

app = Flask(__name__)

# Queue for tasks
task_queue = queue.Queue(maxsize=3)

# Dictionary to store task status
tasks = {}

def translate_speech(file_path, task_id):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        tasks[task_id]['status'] = 'finished'
        tasks[task_id]['result'] = result['text']
    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['result'] = str(e)

def task_processor():
    while True:
        task_id, file_path = task_queue.get()
        translate_speech(file_path, task_id)

# Start the task processor in a separate thread
thread = threading.Thread(target=task_processor, daemon=True)
thread.start()

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    if task_queue.full():
        return jsonify({"error": "Queue limit reached"}), 429

    file = request.files['file']
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"upload-{timestamp}{file_extension}"
    file_path = os.path.join("uploads/", filename)
    file.save(file_path)

    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending', 'result': None}
    task_queue.put((task_id, file_path))

    return jsonify({"task_id": task_id}), 202

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    if task_id in tasks:
        return jsonify(tasks[task_id])
    else:
        return jsonify({"error": "Invalid task ID"}), 404
    
@app.route('/result/<task_id>', methods=['GET'])
def result(task_id):
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
    app.run(debug=True)