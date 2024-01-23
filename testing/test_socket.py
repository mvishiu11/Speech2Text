import os
import websockets
import asyncio
import requests
import time
import pytest

BASE_URL = "http://127.0.0.1:" + os.environ.get("PORT", "8000")

@pytest.fixture(scope='module')
def audio_file_path():
    # setup
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Navigate two levels up from the current file
    path = os.path.join(base_dir, "examples", "example_eng_1.wav")
    yield path
    # teardown (if any)

@pytest.mark.asyncio
async def test_websocket(audio_file_path):
    audio_settings = {"sample_rate": 45000,
            "bit_depth": 16,
            "channels": 1}
    
    print(f"Setting sample rate to {audio_settings['sample_rate']}...")
    response = requests.post(BASE_URL + "/ws/audio_settings", json=audio_settings)
    print("Response:", response)
    assert response.status_code != 422, "Failed to set sample rate. Quitting the test..."
    
    assert response.status_code == 200
    assert response.json().get("sample_rate") == audio_settings["sample_rate"]
    assert response.json().get("bit_depth") == audio_settings["bit_depth"]
    assert response.json().get("channels") == audio_settings["channels"]
    
    uri = "ws://localhost:8000/ws/test"
    print(f"Opening a websocket connection to {uri}...")
    async with websockets.connect(uri) as websocket:
            try:
                with open(audio_file_path, 'rb') as file:
                    print("Reading file...")
                    wav_bytes = file.read()
                    
                response = await websocket.send(wav_bytes)
                print(f"Sent chunk {2}, response: {response}")
                wav_response = await websocket.recv()
                print(f"Received response: {wav_response}")
                task_id = wav_response
                
                while True:
                    response = requests.get(f"{BASE_URL}/status/{task_id}")
                    print(response.json())
                    if response.json()["status"] == "finished":
                        break
                    elif response.json()["status"] == "failed":
                        get_response = requests.get(f"{BASE_URL}/result/{task_id}")
                        print(f"Failed to translate file. Error: {get_response.json()['error']}")
                        return
                    time.sleep(1)
                print("Translation completed.")
                get_response = requests.get(f"{BASE_URL}/result/{task_id}")
                print(get_response.json())
                text = get_response.json()["text"]
                print("Text: " + text)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection closed: {e}")

            print("Test completed.")