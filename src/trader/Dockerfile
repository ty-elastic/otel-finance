FROM python:3.12.6-slim-bookworm

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# add OTel auto-instrumentation libs matching installed Python modules
RUN opentelemetry-bootstrap -a install

COPY app.py .
COPY baggage_log_processor.py .

EXPOSE 9000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "9000"]