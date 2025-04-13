package com.example.app

import android.os.Bundle
import android.view.View
import android.widget.Button
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import com.example.app.trading.TradingService

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        val tradeService = TradingService(applicationContext)

        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.main_activity)

        val requestTrade = findViewById(R.id.request_trade) as Button
        requestTrade.setOnClickListener(View.OnClickListener { _: View? ->
            tradeService.tradeRequest()
        })

        val generateException = findViewById(R.id.generate_exception) as Button
        generateException.setOnClickListener(View.OnClickListener { _: View? ->
            tradeService.generateException()
        })
    }
}
