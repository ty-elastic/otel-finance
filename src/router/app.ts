/*app.ts*/
import express, { Express } from 'express';
import type { Request, Response } from 'express';

import { createProxyMiddleware } from 'http-proxy-middleware';

const PORT: number = parseInt(process.env.PORT || '9000');
const app: Express = express();

function getRandomBoolean() {
  return Math.random() < 0.5;
}

function customRouter(req: any) {
  if (req.query.service != null) {
    return `http://${req.query.service}:9003`;
  }
  else {
    if (req.query.canary === 'true')
      return `http://${process.env.RECORDER_HOST_CANARY}:9003`;
    else {
      if (process.env.RECORDER_HOST_2 == null)
        return `http://${process.env.RECORDER_HOST_1}:9003`;
      else if (getRandomBoolean())
        return `http://${process.env.RECORDER_HOST_1}:9003`;
      else
        return `http://${process.env.RECORDER_HOST_2}:9003`;
    }
  }
};

const proxyMiddleware = createProxyMiddleware<Request, Response>({
  router: customRouter,
  changeOrigin: false
})

app.use('/', proxyMiddleware);

app.get('/health', (req, res) => {
  res.send("KERNEL OK")
});

app.listen(PORT, () => {
  console.log(`Listening for requests on http://localhost:${PORT}`);
});
