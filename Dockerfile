FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt -y update
RUN apt -y upgrade
RUN apt -y install ffmpeg
COPY . .
CMD ["python3", "vinyl.py"]
