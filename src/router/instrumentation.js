/*
 * Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
 * or more contributor license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright
 * ownership. Elasticsearch B.V. licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

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
const path = require('path');

// TODO see isMainThread and module.register usage in require.js

const {
    ElasticNodeSDK,
} = require('@elastic/opentelemetry-node/sdk');

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