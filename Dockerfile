FROM python:3.11.5
RUN apt-get update && apt-get install -y ffmpeg
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
