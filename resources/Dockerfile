FROM python:3.12.6-slim-bookworm

WORKDIR /python-docker

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY *.py ./

COPY context context
COPY alias alias
COPY kibana kibana
COPY ml ml
COPY slo slo
COPY assistant assistant

EXPOSE 9010
CMD [ "flask", "run", "--host=0.0.0.0", "-p", "9010" ]