FROM python:3.12.6-slim-bookworm

WORKDIR /python-docker

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# add OTel libs
RUN pip3 install --root-user-action=ignore elastic-opentelemetry opentelemetry-processor-baggage
COPY lib/ .
RUN pip3 install --root-user-action=ignore -e baggage-log-record-processor

COPY app.py .

# add OTel auto-instrumentation libs matching installed Python modules
RUN opentelemetry-bootstrap -a install

ENV TRADER_HOST="trader"

EXPOSE 9002
CMD [ "opentelemetry-instrument", "--logs_exporter", "otlp", "flask", "run", "--host=0.0.0.0", "-p", "9002" ]