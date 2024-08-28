FROM python:3.10-slim-bullseye
RUN mkdir /ictai
COPY requirements.txt /ictai
COPY config.yaml /ictai
COPY util/ /ictai/
COPY templates/ /ictai/
COPY *.py /ictai
WORKDIR /ictai
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
CMD python web.py
