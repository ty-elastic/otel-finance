package com.example.app

import android.app.Application
import co.elastic.apm.android.sdk.ElasticApmAgent
import co.elastic.apm.android.sdk.ElasticApmConfiguration
import co.elastic.apm.android.sdk.traces.http.HttpTraceConfiguration
import co.elastic.apm.android.sdk.traces.http.attributes.HttpAttributesVisitor
import co.elastic.apm.android.sdk.traces.http.data.HttpRequest
import co.elastic.apm.android.truetime.TrueTime
import com.example.app.trading.TradingService
import io.opentelemetry.api.GlobalOpenTelemetry
import io.opentelemetry.api.common.AttributesBuilder
import io.opentelemetry.instrumentation.logback.appender.v1_0.OpenTelemetryAppender
import kotlinx.coroutines.runBlocking
import org.slf4j.LoggerFactory
import java.util.Random
import java.util.Timer
import java.util.TimerTask


class MainApp : Application() {


    companion object {
        private val log = LoggerFactory.getLogger("Trader")
        fun findParameterValue(parameterName: String, query: String): String? {
            return query.split('&').map {
                val parts = it.split('=')
                val name = parts.firstOrNull() ?: ""
                val value = parts.drop(1).firstOrNull() ?: ""
                Pair(name, value)
            }.firstOrNull{it.first == parameterName}?.second
        }
    }

    class MyHttpAttributesVisitor : HttpAttributesVisitor {
        override fun visit(attrsBuilder: AttributesBuilder, request: HttpRequest) {
            val customerId = findParameterValue("customer_id", request.url.query) as String
            log.warn("here")
            log.warn(customerId)

            attrsBuilder.put("customer_id", customerId);
        }
    }

    fun handleUncaughtException (thread: Thread , e: Throwable) {}

    override fun onCreate() {
        super.onCreate()

        // Setup handler for uncaught exceptions.
        Thread.setDefaultUncaughtExceptionHandler { thread, e ->
            handleUncaughtException(
                thread,
                e
            )
        }

        val httpConfig = HttpTraceConfiguration.builder()
            .addHttpAttributesVisitor(MyHttpAttributesVisitor())
            .build()
        val configuration = ElasticApmConfiguration.builder()
            .setHttpTraceConfiguration(httpConfig)
            .build()

        ElasticApmAgent.initialize(this, configuration);

        // install logback logging hook
        val sdk = GlobalOpenTelemetry.get()
        OpenTelemetryAppender.install(sdk);

        TrueTime.clearCachedInfo()

        val rand = Random()
        val tradeService = TradingService(applicationContext)

        val delay = 1000
        val period = 10000
        val timer = Timer()
        timer.schedule(object : TimerTask() {
            override fun run() {
                        try {

                            // generate exception 10% of the time
                            if (rand.nextInt(10) == 0) {
                               tradeService.generateException()
                            } else {
                                tradeService.tradeRequest()
                                log.info("HERE!!")
                            }
                        } catch (exception: Exception) {
                            val exceptionHandler = Thread.getDefaultUncaughtExceptionHandler()
                            exceptionHandler?.uncaughtException(Thread.currentThread(), exception)
                        }

            }
        }, delay.toLong(), period.toLong())
    }
}