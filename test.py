import requests
import time

# URL of the Flask app
BASE_URL = "http://127.0.0.1:5000"

def test_translation(file_path):
    # Step 1: Send a POST request to the /translate endpoint
    with open(file_path, 'rb') as file:
        response = requests.post(f"{BASE_URL}/translate", files={'file': file})

    # Check if the POST request was successful
    if not (200 >= response.status_code < 300):
        print(f"Failed to submit file for translation. Status Code: {response.status_code}")
        print(response.json())
        return

    # Step 2: Save the transcribed file to /runs folder
    file_name = file_path.split("\\")[-1].split(".")[0] + ".txt"
    print(file_name)
    with open(f"runs\{file_name}", "w") as file:
        file.write(response.json()["text"])
    
    
if __name__ == "__main__":
    test_translation("examples\example_eng_1.wav")
    time.sleep(5)  # Wait for the task to complete
    print("Done!")