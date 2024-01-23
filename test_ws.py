import os
import websockets
import asyncio
import requests
import time

BASE_URL = "http://127.0.0.1:" + os.environ.get("PORT", "8000")

async def test_websocket():
    audio_settings = {"sample_rate": 45000,
            "bit_depth": 16,
            "channels": 1}
    
    print(f"Setting sample rate to {audio_settings['sample_rate']}...")
    response = requests.post("http://localhost:8000/ws/audio_settings", json=audio_settings)
    print("Response:", response)
    if response.status_code == 422:
        print("Failed to set sample rate. Quiting the test...")
        return
    
    assert response.status_code == 200
    assert response.json().get("sample_rate") == audio_settings["sample_rate"]
    assert response.json().get("bit_depth") == audio_settings["bit_depth"]
    assert response.json().get("channels") == audio_settings["channels"]
    
    uri = "ws://localhost:8000/ws/test"
    print(f"Opening a websocket connection to {uri}...")
    async with websockets.connect(uri) as websocket:
            try:
                with open('examples\example_eng_1.wav', 'rb') as file:
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
        
asyncio.run(test_websocket())
