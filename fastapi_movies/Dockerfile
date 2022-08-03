FROM python:3.10-buster

RUN  groupadd -r runner --gid=1280 && useradd -r -g runner --uid=1280 --create-home --shell /bin/bash runner

COPY ./requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src /home/runner/
USER runner
WORKDIR /home/runner

CMD gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$FAST_API_PORT
EXPOSE $FAST_API_PORT