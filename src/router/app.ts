/*app.ts*/
import express, { Express } from 'express';
import type { Request, Response } from 'express';

import { createProxyMiddleware } from 'http-proxy-middleware';

const PORT: number = parseInt(process.env.PORT || '9000');
const app: Express = express();

const pathFilterCanary = function (path: string, req: express.Request) {
  console.log(req.query.canary)
  return req.query.canary === 'True'
};

const proxyMiddleware1 = createProxyMiddleware<Request, Response>({
  target: 'http://127.0.0.1:9003',
  changeOrigin: false,
})

const proxyMiddleware2 = createProxyMiddleware<Request, Response>({
  target: 'http://127.0.0.1:9004',
  pathFilter: pathFilterCanary,
  changeOrigin: false,
})

app.use('/', proxyMiddleware1);
app.use('/', proxyMiddleware2);

app.listen(PORT, () => {
  console.log(`Listening for requests on http://localhost:${PORT}`);
});
