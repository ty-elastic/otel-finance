FROM python:3.12.6-slim-bookworm

WORKDIR /python-docker

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY *.py .
COPY context .
COPY alias .
COPY kibana .
COPY ml .
COPY slo .

EXPOSE 9010
CMD [ "flask", "run", "--host=0.0.0.0", "-p", "9010" ]