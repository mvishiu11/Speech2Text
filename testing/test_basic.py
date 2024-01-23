import requests
import time
import os
import pytest

# URL of the Flask app
BASE_URL = "http://127.0.0.1:" + os.environ.get("PORT", "8000")

@pytest.fixture(scope='module')
def file_path():
    # setup
    base_dir = os.path.dirname(os.path.dirname(__file__))  # This will navigate two levels up from the current file
    path = os.path.join(base_dir, "examples", "example_eng_1.wav")
    yield path
    # teardown (if any)

def test_translation(file_path):
    print(f"Sending a POST request to {BASE_URL}/translate...")
    # Step 1: Send a POST request to the /translate endpoint
    with open(file_path, 'rb') as file:
        response = requests.post(f"{BASE_URL}/translate", files={'file': file})
    
    assert response.status_code != 429, "Queue limit reached. Try again later."
    assert response.status_code != 400, "No file part."
    assert 200 <= response.status_code < 300, f"Failed to submit file for translation. Status Code: {response.status_code}, Response: {response}"

    # Step 2: Get a result of the translation using a GET requests to the /status and /result endpoints
    task_id = response.json()["task_id"]
    while True:
        response = requests.get(f"{BASE_URL}/status/{task_id}")
        status = response.json()["status"]
        assert status != "failed", f"Failed to translate file. Error: {response.json()}"
        if status == "finished":
            break
        time.sleep(1)
    
    get_response = requests.get(f"{BASE_URL}/result/{task_id}")
    text = get_response.json()["text"]

    # Step 3: Save the transcribed file to /runs folder
    file_name = os.path.basename(file_path).split(".")[0] + "_test.txt"
    runs_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), "runs")
    output_file_path = os.path.join(runs_dir, file_name)
    with open(output_file_path, "w") as file:
        file.write(text)

    # Additional assertions can be added here to verify the output
