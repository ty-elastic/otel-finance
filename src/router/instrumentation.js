/**
 * Setup and start the Elastic OpenTelemetry Node.js SDK distro.
 *
 * This is an alternative to the typical `node -r @elastic/opentelemetry-node`
 * convenience for starting the SDK. Starting the SDK manually via a local
 * file can be useful to allow configuring the SDK with code.
 *
 * Usage:
 *      node -r ./start-elastic-sdk.js SCRIPT.js
 */

const os = require('os');

const { ElasticNodeSDK } = require('@elastic/opentelemetry-node/sdk');
const { tracing } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { ALLOW_ALL_BAGGAGE_KEYS, BaggageSpanProcessor } = require('@opentelemetry/baggage-span-processor');

const spanProcessors = [
    new tracing.BatchSpanProcessor(
      new OTLPTraceExporter()),
    new BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS)];

const sdk = new ElasticNodeSDK({
    spanProcessors
});

process.on('SIGTERM', async () => {
    try {
        await sdk.shutdown();
    } catch (err) {
        console.warn('warning: error shutting down OTel SDK', err);
    }
    process.exit(128 + os.constants.signals.SIGTERM);
});

process.once('beforeExit', async () => {
    // Flush recent telemetry data if about the shutdown.
    try {
        await sdk.shutdown();
    } catch (err) {
        console.warn('warning: error shutting down OTel SDK', err);
    }
});

sdk.start();