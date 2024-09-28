/*
 * Copyright The OpenTelemetry Authors
 * SPDX-License-Identifier: Apache-2.0
 */

package com.example.baggage.logrecord.processor;

import io.opentelemetry.sdk.autoconfigure.spi.AutoConfigurationCustomizer;
import io.opentelemetry.sdk.autoconfigure.spi.AutoConfigurationCustomizerProvider;
import io.opentelemetry.sdk.autoconfigure.spi.ConfigProperties;
import io.opentelemetry.sdk.logs.SdkLoggerProviderBuilder;
import java.util.List;

public class BaggageLogRecordProcessorCustomizer implements AutoConfigurationCustomizerProvider {
  @Override
  public void customize(AutoConfigurationCustomizer autoConfigurationCustomizer) {
    autoConfigurationCustomizer.addLoggerProviderCustomizer(
        (sdkLoggerProviderBuilder, config) -> {
          addLogRecordProcessor(sdkLoggerProviderBuilder, config);
          System.out.println("TESTING!!!!!!!!!!!!!!!!");
          return sdkLoggerProviderBuilder;
        });
  }

  private static void addLogRecordProcessor(
    SdkLoggerProviderBuilder sdkLoggerProviderBuilder, ConfigProperties config) {
      sdkLoggerProviderBuilder.addLogRecordProcessor(createProcessor());
  }

  static BaggageLogRecordProcessor createProcessor() {
    return new BaggageLogRecordProcessor();
  }
}
