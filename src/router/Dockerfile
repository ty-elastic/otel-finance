FROM node:20-alpine

RUN mkdir -p /home/node/app/node_modules
WORKDIR /home/node/app

COPY package*.json ./
COPY tsconfig.json ./
COPY app.ts ./
COPY instrumentation.js ./

RUN npm install
RUN npm install --save @opentelemetry/baggage-span-processor

ENV OTEL_SERVICE_NAME="router"
ENV OTEL_EXPERIMENTAL_RESOURCE_DETECTORS="process_runtime"

EXPOSE 9000

CMD [ "npx", "ts-node", "-r", "./instrumentation.js", "app.ts"]
