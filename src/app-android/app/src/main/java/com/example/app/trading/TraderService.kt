package com.example.app.trading

import retrofit2.http.POST
import retrofit2.http.Query

interface TraderService {
    @POST("/trader/trade/request")
    fun tradeRequest(@Query("symbol") symbol: String,
                             @Query("day_of_week") dayOfWeek: String ,
                             @Query("customer_id") customerId: String ,
                             @Query("region") region: String ,
                             @Query("data_source") dataSource: String
    ): retrofit2.Call<Void>

    @POST("/trader/trade/unknown")
    fun tradeUnkown(): retrofit2.Call<Void>

}