FROM python:3.12

WORKDIR /usr/src/app
COPY ./tg-techsupport-bot ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./config ./config
CMD [ "python", "./run.py" ]
