/*
 * Copyright The OpenTelemetry Authors
 * SPDX-License-Identifier: Apache-2.0
 */

package com.example.baggage.logrecord.processor;

import io.opentelemetry.api.baggage.Baggage;
import io.opentelemetry.context.Context;
import io.opentelemetry.sdk.logs.LogRecordProcessor;
import io.opentelemetry.sdk.logs.ReadWriteLogRecord;
import io.opentelemetry.api.common.AttributeKey;

public class BaggageLogRecordProcessor implements LogRecordProcessor {

  @Override
  public void onEmit(Context context, ReadWriteLogRecord logRecord) {
      // add baggage to log attributes
      Baggage baggage = Baggage.fromContext(context);
      baggage.forEach(
              (key, value) -> logRecord.setAttribute(
                      // add prefix to key to not override existing attributes
                      AttributeKey.stringKey(key),
                      value.getValue()));
  }
}
