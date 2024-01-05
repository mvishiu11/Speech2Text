from flask import Flask, request, jsonify
import whisper
import datetime
import os

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # Generating a timestamp for the file name
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{timestamp}{file_extension}"

    file_path = os.path.join(".\\uploads\\", filename)  # Update path as needed
    file.save(file_path)

    text = translate_speech(file_path)
    return jsonify({"text": text})

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error here
    return jsonify({"error": str(e)}), 500

def translate_speech(file_path):
    model = whisper.load_model("base")  # Use an appropriate model size
    result = model.transcribe(file_path)
    return result["text"]

if __name__ == "__main__":
    app.run(debug=True)  # debug=True enables development mode