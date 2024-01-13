import os
import websockets
import asyncio


async def test_websocket():
    uri = "ws://localhost:8000/ws/test"
    async with websockets.connect(uri) as websocket:
        for i in range(5):
            fake_audio_chunk = os.urandom(1024)
            await websocket.send(fake_audio_chunk)
            print(f"Sent chunk {i+1}")

            try:
                response = await websocket.recv()
                print(f"Received response: {response}")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                break

        print("Test completed.")
        
asyncio.run(test_websocket())
