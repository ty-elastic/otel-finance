package com.example.app.trading

import android.content.Context
import com.example.app.R
import io.embrace.android.embracesdk.Embrace
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient

import retrofit2.Call
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class TradingService(context: Context) {

    private val traderService: TraderService by lazy {
        val httpClient = OkHttpClient.Builder().build()

        val tradeService = Retrofit.Builder()
            .baseUrl(context.getString(R.string.trade_url))
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        tradeService.create(TraderService::class.java)
    }

    fun tradeRequest() {

        val activityLoad = Embrace.getInstance().createSpan("tradeRequest")

        val call = traderService.tradeRequest(symbol = "Ty", dayOfWeek = "F", customerId = "tbekiares", region = "NA", dataSource = "customer")
        call.enqueue(object: retrofit2.Callback<Void> {
            override fun onResponse(p0: Call<Void>, p1: Response<Void>) {
                activityLoad?.stop();
            }

            override fun onFailure(p0: Call<Void>, p1: Throwable) {
                activityLoad?.stop();
            }
        })
    }

    fun generateException() {

        val call = traderService.tradeUnkown()
        call.enqueue(object: retrofit2.Callback<Void> {
            override fun onResponse(p0: Call<Void>, p1: Response<Void>) {

            }

            override fun onFailure(p0: Call<Void>, p1: Throwable) {

            }
        })
    }

}