FROM python:slim
LABEL authors="arthur"

RUN apt update && apt upgrade -y && apt install ffmpeg -y

COPY ./bot/ ./bot/
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "-m", "bot.main"]