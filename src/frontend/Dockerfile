FROM node:latest as frontend

ARG ELASTIC_APM_SERVER_RUM_ENDPOINT
ARG ELASTIC_APM_SERVER_RUM_CREDENTIALS
ARG KIBANA_URL
ARG ELASTICSEARCH_USER
ARG ELASTICSEARCH_PASSWORD

WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY trader-app/package*.json ./
# Install dependencies
RUN npm install

COPY trader-app/ .

ENV SERVICE_VERSION=1.0.0
ENV SERVICE_NAME=trader-app

RUN echo "\
    import { init as initApm } from '@elastic/apm-rum' \n\
    const apm = initApm({ \n\
        serviceName: '${SERVICE_NAME}', \n\
        serverUrl: '${ELASTIC_APM_SERVER_RUM_ENDPOINT}', \n\
        sendCredentials: ${ELASTIC_APM_SERVER_RUM_CREDENTIALS}, \n\
        serviceVersion: '${SERVICE_VERSION}', \n\
        environment: '' \n\
    }) \n\
    export default apm; \n\
" > src/rum.js
RUN echo "import apm from './rum'\n" | cat - src/index.js > temp && mv temp src/index.js

RUN npm run build

ENV KIBANA_URL=$KIBANA_URL
ENV ELASTICSEARCH_USER=$ELASTICSEARCH_USER
ENV ELASTICSEARCH_PASSWORD=$ELASTICSEARCH_PASSWORD

COPY upload_source_map.sh build/
RUN cd build && \
    ./upload_source_map.sh

CMD rm -rf /build/* && cp -r /app/build/. /build/