# Speech-to-Text API with Whisper

## Table of Contents

- [Project Overview](#project-overview)
- [Requirements and Setup](#requirements-and-setup)
- [Using the Application](#using-the-application)
- [Dockerization](#dockerization)
- [Example Usage](#example-usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This Speech-to-Text API utilizes OpenAI's Whisper model to transcribe spoken language in audio files to text. It's designed to be simple, efficient, and easy to integrate into existing systems.

### To Do
- [ ] Implement asynchronous processing for handling multiple requests.
- [ ] Add support for more languages and dialects.
- [ ] Enhance error handling and logging.

## Requirements and Setup

To use the Speech-to-Text API, you need the following:

- Python 3.8 or higher
- FFmpeg (for audio processing)

To set up the application:

1. Clone the repository to your local machine.
2. (Optional) Create a virtual environment for the application.
An example using conda:
- Create the environment:
```bash
conda create -n speech-to-text-api python=3.8
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

To run the Flask app, execute the following command:

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`. It listens for POST requests to the `/translate` endpoint. To use it, send a POST request with an audio file in ``.wav` format. The file should be included in the request's body as form-data. The server will process this file and return the transcribed text as a JSON response.

Example of a POST request using curl:

```bash
curl -X POST -F "file=@/path/to/audio/file.wav" http://127.0.0.1:5000/translate
```

Replace `path_to_audio_file.wav` with the path to your audio file. The API will return a JSON response containing the transcribed text.

## Dockerization

To run the application in a Docker container, you need to have Docker installed on your machine. To build the Docker image, run the following command:

```bash
docker build -t speech-to-text-api .
```

To run the container, execute the following command:

```bash
docker run -p 5000:5000 speech-to-text-api
```

The application will start on `http://127.0.0.1:5000`. You can now send POST requests to the `/translate` endpoint.

## Example Usage

There is an example provided via the [test.py](test.py) script, which uses the [requests](https://docs.python-requests.org/en/master/) library to send a POST request to the API and save the response to the `runs\` directory as a text file. To run the example, execute the following command:

```bash
python test.py
```

## Contributing

Contributions to the project are welcome. Please follow the standard fork-and-pull request workflow. For any and all questions, please contact me [here](mailto:jakub.m.muszynski@gmail.com).

## License

This project is licensed under the terms of the [MIT License](LICENSE).
This might change in the future.
