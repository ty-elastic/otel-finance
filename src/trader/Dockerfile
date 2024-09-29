FROM python:3.12.6-slim-bookworm

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# add OTel libs
RUN pip3 install elastic-opentelemetry opentelemetry-processor-baggage
# add OTel auto-instrumentation libs matching installed Python modules
RUN opentelemetry-bootstrap -a install

RUN pip3 install -e ../lib/python/baggage-log-record-processor 

COPY app.py .
COPY model.py .

EXPOSE 9001
CMD [ "opentelemetry-instrument", "--logs_exporter", "otlp", "flask", "run", "--host=0.0.0.0", "-p", "9001" ]
