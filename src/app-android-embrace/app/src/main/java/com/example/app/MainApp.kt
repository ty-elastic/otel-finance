package com.example.app

import android.app.Application
import com.example.app.trading.TradingService

import io.embrace.android.embracesdk.Embrace

import java.util.Random
import java.util.Timer
import java.util.TimerTask


class MainApp : Application() {

    fun handleUncaughtException (thread: Thread , e: Throwable) {}

    override fun onCreate() {
        super.onCreate()
        Embrace.getInstance().start(this)

        // Setup handler for uncaught exceptions.
        Thread.setDefaultUncaughtExceptionHandler { thread, e ->
            handleUncaughtException(
                thread,
                e
            )
        }


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
                            }
                        } catch (exception: Exception) {
                            val exceptionHandler = Thread.getDefaultUncaughtExceptionHandler()
                            exceptionHandler?.uncaughtException(Thread.currentThread(), exception)
                        }

            }
        }, delay.toLong(), period.toLong())
    }
}