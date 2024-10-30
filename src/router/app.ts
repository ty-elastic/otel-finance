/*app.ts*/
import express, { Express } from 'express';
import type { Request, Response } from 'express';

import { createProxyMiddleware } from 'http-proxy-middleware';

const PORT: number = parseInt(process.env.PORT || '9000');
const app: Express = express();

const pathFilterCanary = function (path: string, req: express.Request) {
  return req.query.canary === 'True'
};

const proxyMiddleware = createProxyMiddleware<Request, Response>({
  target: `http://${process.env.RECORDER_HOST}:9003`,
  changeOrigin: false,
})

const proxyMiddlewareCanary = createProxyMiddleware<Request, Response>({
  target: `http://${process.env.RECORDER_HOST_CANARY}:9004`,
  pathFilter: pathFilterCanary,
  changeOrigin: false,
})

app.use('/', proxyMiddlewareCanary);
app.use('/', proxyMiddleware);

app.get('/health', (req, res) => {
  res.send("KERNEL OK")
});

app.listen(PORT, () => {
  console.log(`Listening for requests on http://localhost:${PORT}`);
});
