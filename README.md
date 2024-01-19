# Speech-to-Text API with Whisper 
![Version](https://img.shields.io/badge/version-1.0.0-orange) ![License](https://img.shields.io/badge/license-CC_BY_NC_SA_4.0-green) ![Python](https://img.shields.io/badge/python-3.11.5-darkblue) ![FFmpeg](https://img.shields.io/badge/ffmpeg-6.1.1-black) ![FastAPI](https://img.shields.io/badge/fastapi-0.108.0-blue) ![Uvicorn](https://img.shields.io/badge/uvicorn-0.21.1-yellow)


## Table of Contents

- [Project Overview](#project-overview)
- [Requirements and Setup](#requirements-and-setup)
- [Using the Application](#using-the-application)
- [Asynchronous Processing](#asynchronous-processing)
- [Websocket](#websocket)
- [Dockerization](#dockerization)
- [Example Usage](#example-usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This Speech-to-Text API utilizes OpenAI's Whisper model to transcribe spoken language in audio files to text. It's designed to be simple, efficient, and easy to integrate into existing systems.

### To Do
- [x] Implement asynchronous processing for handling multiple requests.
- [x] Add Docker support.
- [X] Use FastAPI instead of Flask.
- [ ] Add database instead of a local queue
- [ ] Add support for more languages and dialects.
- [1/3] Enhance error handling and logging.
- [ ] Add support for more audio formats.
- [ ] Add support for streaming audio.
- [ ] Add support for audio files with multiple speakers.
- [ ] Switch to a more flexible model selection system, probably via Deepgram.

## Requirements and Setup

To use the Speech-to-Text API, you need the following:

- Python 3.11.5 (other versions might work as well, but were not tested)
- FFmpeg (for audio processing)

To set up the application:

1. Clone the repository to your local machine.
2. (Optional) Create a virtual environment for the application.
An example using conda:
- Create the environment:
```bash
conda create -n speech-to-text-api python=3.11.5
```
- Activate the environment:
```bash
conda activate speech-to-text-api
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Using the Application

To run the FastAPI server, execute the following command:

```bash
python run.py [--debug] [--port <port_num>] [--host <host_address>] [--noreload]
```

Possible arguments are:
- `--debug` - run the server in DEBUG mode, which allows for logging DEBUG level content
- `--port <port_num>` - specify the port on which the server will run, default is `8000`, must be an integer s. t. `0 < port_num < 65536`
- `--noreload` - disable auto-reload of the server, default is `False`, currently this will not allow you to disable the server with Ctrl+C, this will be fixed in the future
- `--host <host_address>` - specify the host address on which the server will run, default is `127.0.0.1`, which is the local server, if you do not know what this means, do not change it, as `run.py` does not currenlty handle errors causeed by invalid host addresses


This runs the provided `run.py` script which serves the API via `uvicorn` and does several other things, like setting logger levels. The application will start on `http://127.0.0.1:8000` unless you specified a custom port with `--host`. It listens for POST requests to the `/translate` endpoint. To use it, send a POST request with an audio file in ``.wav` format. The file should be included in the request's body as form-data. 

Example of a POST request using curl:

```bash
curl -X POST -F "file=@/path/to/audio/file.wav" http://127.0.0.1:8000/translate
```

Replace `path_to_audio_file.wav` with the path to your audio file. The return format is JSON, and the response will contain the task ID of the translation task:
    
```json
    {
    "task_id": "b2f7e7e0-9f9b-4e4e-8f4a-9b9b9b9b9b9b"
    }
```

## Asynchronous Processing

The Speech-to-Text API uses a queue which processes translation requests made asynchronously, thus providing a more efficient way to manage multiple translation requests. This is particularly beneficial when dealing with a high volume of requests or large audio files. The queue is currently implemented using Pythons in-built `queue` type, and it is defined locally in the `app.py` file. The queue is limited to 3 concurrent translation tasks for ease of testing, but this limit will be made configurable in the future. Due to this implementation, there are some extra steps involved in using the API, which are described below. I know it may seem like an overkill, but trust me it has a purpose.

### Submitting Translation Requests

When a POST request is sent to the `/translate` endpoint with an audio file, the file is added to a processing queue, and a unique task ID is generated and returned. This ID is used to track the status and result of the translation.

Example of submitting a translation request using `curl`:

```bash
curl -X POST -F "file=@/path/to/audio/file.wav" http://127.0.0.1:8000/translate
```

The response will contain the task ID of the translation task as mentioned in the section above:

```json
    {
    "task_id": "b2f7e7e0-9f9b-4e4e-8f4a-9b9b9b9b9b9b"
    }
```

### Checking Translation Status

To check the status of a translation, a GET request is sent to the `/status/<task_id>` endpoint, where `<task_id>` is the unique ID returned from the POST request.

Example of checking the translation status:
    
```bash
curl http://127.0.0.1:5000/status/b2f7e7e0-9f9b-4e4e-8f4a-9b9b9b9b9b9b
```

The response will contain the status of the translation task:

```json
    {
    "status": "pending"
    }
```

The possible status values are:

- `pending` - the translation task is in the processing queue.
- `finished` - the translation task has been completed.
- `failed` - the translation task has failed.

### Retrieving Translation Results

To retrieve the results of a translation, a GET request is sent to the `/result/<task_id>` endpoint, where `<task_id>` is the unique ID returned from the POST request.

Example of retrieving the translation results:
    
```bash
curl http://127.0.0.1:5000/result/b2f7e7e0-9f9b-4e4e-8f4a-9b9b9b9b9b9b
```

The response will contain the results of the translation task:

```json
    {
    "result": "This is a test."
    }
```

This request will return the translated text if the translation was successful. If the translation failed or if the task has not yet finished, an appropriate error message will be returned.

### Queue Limit Handling

The API is designed to handle a maximum of 3 concurrent translation tasks. If a POST request is made when the queue is full, the API will respond with a `429` status code indicating that the queue limit has been reached. In such cases, it is advisable to retry the request after some time. Currently this limit is hard-coded, but it will be made configurable in the future. 

### Local Queue Definition

Be warned that the queue is defined locally, so if the application is running on multiple machines, the queue will not be shared between them. This means that if a POST request is made to one machine, and then another POST request is made to a different machine, the second request will not be added to the queue. This is a limitation of the current implementation, and it will be addressed in the future. Additionally, the queue is not persistent, so if the application is restarted, the queue will be cleared.

## Websocket

### Connecting to the Websocket

The Speech-to-Text API also supports Websocket connections. To use it, send a request to the `ws://localhost:8000/ws/test` endpoint with an audio file in `.wav` format. The file should be included in the request's body as form-data.

Example of a websocket connection using `websockets` package in Python:

```python
    async with websockets.connect(uri) as websocket:
        fake_audio_chunk = os.urandom(1024)
        await websocket.send(fake_audio_chunk)
        response = await websocket.recv()
```

Few things to note here:

- The endpoint (uri) should be set to `ws://localhost:8000/ws/test`.
- The connection is established using an asynchronous context manager. This is the preffered way of establishing a connection, as it allows for automatic closing of the connection.
- The audio file is sent as a binary string.
- The response is a JSON string containing the task ID of the translation task:

```json
    {
    "task_id": "b2f7e7e0-9f9b-4e4e-8f4a-9b9b9b9b9b9b"
    }
```

- The connection is closed automatically after the response is received, thanks to the context manager.

### Checking Translation Status and Retrieving Translation Results

To check the status of a translation, a GET request is sent to the `/status/<task_id>` endpoint, where `<task_id>` is the unique ID returned from the POST request. The response will contain the status of the translation task:

```json
    {
    "status": "pending"
    }
```

When the status returned is `finished`, the translation results can be retrieved by sending a GET request to the `/result/<task_id>` endpoint, where `<task_id>` is the unique ID returned from the POST request. The response will contain the results of the translation task:

```json
    {
    "result": "This is a test."
    }
```

A more detailed explanation of possible status values and error handling can be found in the [Asynchronous Processing](#asynchronous-processing) section. For more information about the Websocket implementation, please refer to the [FastAPI documentation](https://fastapi.tiangolo.com/advanced/websockets/).




## Dockerization

To run the application in a Docker container, you need to have Docker installed on your machine. To build the Docker image, run the following command:

```bash
docker build -t speech-to-text-api .
```

To run the container, execute the following command:

```bash
docker run -p 8000:8000 speech-to-text-api
```

The application will start on `http://127.0.0.1:8000`. You can now send POST requests to the `/translate` endpoint.

## Example Usage

There is an example provided via the [test.py](test.py) script, which uses the [requests](https://docs.python-requests.org/en/master/) library to send a POST request to the API and save the response to the `runs\` directory as a text file. To run the example, execute the following command:

```bash
python test.py
```

There are also two additional example files called `test_ws.py` and `test_async.ws` which demonstrate the use of the Websocket connection and asynchronous usage of the API respectively. To run the `test_ws.py`, execute the following command:

```bash
python test_ws.py
```

And to run the `test_async.py`, execute the following command:

```bash
python test_async.py
```

## Contributing

Contributions to the project are welcome. Please follow the standard fork-and-pull request workflow. For any and all questions, please contact me [here](mailto:jakub.m.muszynski@gmail.com).

## License

This project is licensed under the terms of the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE).
This might change in the future.