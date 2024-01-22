import os
import websockets
import asyncio
import requests
import time

BASE_URL = "http://127.0.0.1:" + os.environ.get("PORT", "8000")

async def test_websocket():
    data = {"sample_rate": 1024}
    
    print("Setting sample rate to 1024...")
    response = requests.post("http://localhost:8000/ws/audio_settings", json=data)
    print("Response:", response)
    if response.status_code == 422:
        print("Failed to set sample rate. Quiting the test...")
        return
    
    assert response.status_code == 200
    assert response.json().get("sample_rate") == data["sample_rate"]
    assert response.json().get("bit_depth") == os.environ.get("BIT_DEPTH", 16)
    assert response.json().get("channels") == os.environ.get("CHANNELS", 1)
    
    uri = "ws://localhost:8000/ws/test"
    print(f"Opening a websocket connection to {uri}...")
    async with websockets.connect(uri) as websocket:
        for i in range(1):
            fake_audio_chunk = os.urandom(1024)
            response = await websocket.send(fake_audio_chunk)
            print(f"Sent chunk {i+1}")

            try:
                response = await websocket.recv()
                print(f"Received response: {response}, type: {type(response)}")
                task_id = response
                
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
                print("Text: " + text)
                
                with open('examples\example_eng_1.wav', 'rb') as file:
                    wav_bytes = file.read()
                    
                response = await websocket.send(wav_bytes)
                print(f"Sent chunk {i+2}")
                wav_response = await websocket.recv()
                task_id = wav_response
                
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
                print("Text: " + text)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                break

        print("Test completed.")
        
asyncio.run(test_websocket())
