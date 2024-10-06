FROM python:3.12.5
# for TTS
RUN apt-get update && apt-get install -y espeak-ng libespeak-ng-dev

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
