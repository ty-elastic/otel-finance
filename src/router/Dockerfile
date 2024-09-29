FROM node:20-alpine

RUN mkdir -p /home/node/app/node_modules
WORKDIR /home/node/app

COPY package*.json ./
COPY tsconfig.json ./
COPY app.ts ./

RUN npm install

EXPOSE 9000

CMD [ "npx", "ts-node", "-r", "@elastic/opentelemetry-node", "app.ts"]