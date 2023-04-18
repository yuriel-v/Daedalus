FROM python:3.9-slim as py
RUN apt-get update && apt-get install -y gcc
WORKDIR /reqs
COPY ./requirements.txt /reqs
RUN pip install -r requirements.txt

FROM python:3.9-slim
WORKDIR /home/daedalus
COPY ./src/ .
COPY --from=py /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages/
ENTRYPOINT python3 ./main.py