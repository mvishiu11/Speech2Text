import requests
import time

# URL of the Flask app
BASE_URL = "http://127.0.0.1:5000"

def send_translation_request(file_path):
    with open(file_path, 'rb') as file:
        response = requests.post(f"{BASE_URL}/translate", files={'file': file})
    return response

def check_translation_status(task_id):
    while True:
        response = requests.get(f"{BASE_URL}/status/{task_id}")
        status = response.json()["status"]
        if status == "finished":
            return response.json()["result"]
        elif status == "failed":
            print(f"Failed to translate file. Error: {response.json()['result']}")
            return None
        time.sleep(1)

def test_translation(file_paths):
    tasks = {}

    # Send multiple translation requests
    for file_path in file_paths:
        response = send_translation_request(file_path)

        # Check if the POST request was successful
        if response.status_code == 429:
                print("Queue limit reached. Try again later.")
                continue
        elif response.status_code == 400:
                print("No file part")
                continue
        elif not (200 <= response.status_code < 300):
            print(f"Failed to submit file for translation. Status Code: {response.status_code}")
            print(response.json())
            continue

        task_id = response.json()["task_id"]
        tasks[task_id] = file_path

    # Check the status of each translation task
    i = 0
    for task_id, file_path in tasks.items():
        i += 1
        text = check_translation_status(task_id)
        if text:
            file_name = file_path.split("\\")[-1].split(".")[0] + f"_{i}" + "_test" + ".txt"
            print(file_name)
            with open(f"runs\{file_name}", "w") as file:
                file.write(text)
            print(f"Translated text saved to runs\{file_name}")

if __name__ == "__main__":
    example_files = ["examples\\example_eng_1.wav", "examples\\example_eng_1.wav", "examples\\example_eng_1.wav"]
    test_translation(example_files)
    print("All tasks completed.")
