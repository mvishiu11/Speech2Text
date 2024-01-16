import os
import websockets
import asyncio
import requests

async def test_websocket():
    data = {"sample_rate": 16000}
    
    print("Setting sample rate to 1024...")
    response = requests.post("http://localhost:8000/ws/sample_rate", json=data)
    print("Response:", response)
    if response.status_code == 422:
        print("Failed to set sample rate. Quiting the test...")
        return
    
    uri = "ws://localhost:8000/ws/test"
    print(f"Opening a websocket connection to {uri}...")
    async with websockets.connect(uri) as websocket:
        for i in range(1):
            fake_audio_chunk = os.urandom(1024)
            response = await websocket.send(fake_audio_chunk)
            print(f"Sent chunk {i+1}")

            try:
                response = await websocket.recv()
                print(f"Received response: {response}")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                break

        print("Test completed.")
        
asyncio.run(test_websocket())
