package com.example.app

import android.os.Bundle
import android.view.View
import android.widget.Button
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import com.example.app.trading.TradingService
import io.opentelemetry.api.GlobalOpenTelemetry
import io.opentelemetry.context.Scope
import org.slf4j.LoggerFactory


class MainActivity : ComponentActivity() {
    private val log = LoggerFactory.getLogger("Trader")

    override fun onCreate(savedInstanceState: Bundle?) {
        val tradeService = TradingService(applicationContext)
        val tracer = GlobalOpenTelemetry.getTracer("ui")

        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.main_activity)

        val requestTrade = findViewById(R.id.request_trade) as Button
        requestTrade.setOnClickListener(View.OnClickListener { _: View? ->
            val span = tracer.spanBuilder("click:tradeRequest").startSpan()
            span.makeCurrent().use { scope ->
                tradeService.tradeRequest()
            }
            span.end()
        })

        val generateException = findViewById(R.id.generate_exception) as Button
        generateException.setOnClickListener(View.OnClickListener { _: View? ->
            tradeService.generateException()

        })
    }
}
