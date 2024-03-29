import requests
import time
import os

# URL of the Flask app
BASE_URL = "http://127.0.0.1:" + os.environ.get("PORT", "8000")

def test_translation(file_path):
    print(f"Sending a POST request to {BASE_URL}/translate...")
    # Step 1: Send a POST request to the /translate endpoint
    with open(file_path, 'rb') as file:
        response = requests.post(f"{BASE_URL}/translate", files={'file': file})
        

    # Check if the POST request was successful
    if response.status_code == 429:
            print("Queue limit reached. Try again later.")
            return
    elif response.status_code == 400:
            print("No file part")
            return
    elif not (200 <= response.status_code < 300):
        print(f"Failed to submit file for translation. Status Code: {response.status_code}")
        print(response)
        return
    
    # Step 2: Get a result of the translation using a GET requests to the /status and /result endpoints
    task_id = response.json()["task_id"]
    while True:
        response = requests.get(f"{BASE_URL}/status/{task_id}")
        if response.json()["status"] == "finished":
            break
        elif response.json()["status"] == "failed":
            print(f"Failed to translate file. Error: {response.json()['result']}")
            return
        time.sleep(1)
    get_response = requests.get(f"{BASE_URL}/result/{task_id}")
    text = get_response.json()["text"]

    # Step 3: Save the transcribed file to /runs folder
    file_name = file_path.split("\\")[-1].split(".")[0] + "_test" + ".txt"
    print(file_name)
    with open(f"runs\{file_name}", "w") as file:
        file.write(text)
    
    
if __name__ == "__main__":
    test_translation(os.path.join("examples", "example_eng_1.wav"))
    print("Done!")