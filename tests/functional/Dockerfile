FROM python:3.10-buster

RUN  groupadd -r runner --gid=1280 && useradd -r -g runner --uid=1280 --create-home --shell /bin/bash runner

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /home/runner/
USER runner
WORKDIR /home/runner

CMD  python3 wait_for_es.py && python3 wait_for_redis.py && pytest src
