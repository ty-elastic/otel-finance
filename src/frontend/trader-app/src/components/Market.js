import React, { useState, useEffect } from 'react';
import axios from "axios";

import MarketTputRegion from './MarketTputRegion'
import MarketTputSymbol from './MarketTputSymbol'
import MarketTputCustomer from './MarketTputCustomer'

import MarketLatencyRegion from './MarketLatencyRegion'

import MarketSkewMarketFactorSymbol from './MarketSkewMarketFactorSymbol'

import MarketCanaryRegion from './MarketCanaryRegion'

import MarketErrModelRegion from './MarketErrModelRegion'
import MarketErrDbRegion from './MarketErrDbRegion'

class Market extends React.Component {
    render() {
        return (
            <div>
                <h1>Manipulate Market</h1>

                <h2>Throughput by Region</h2>
                <MarketTputRegion/>
                <hr></hr>
                <h2>Throughput by Symbol</h2>
                <MarketTputSymbol/>
                <hr></hr>
                <h2>Throughput by Customer</h2>
                <MarketTputCustomer/>
                <hr></hr>

                <h2>Model Error by Region</h2>
                <MarketErrModelRegion/>
                <hr></hr>

                <h2>DB Error by Region</h2>
                <MarketErrDbRegion/>
                <hr></hr>

                <h2>Latency by Region</h2>
                <MarketLatencyRegion/>
                <hr></hr>

                <h2>Canary by Region</h2>
                <MarketCanaryRegion/>
                <hr></hr>

                <h2>Skew Market Factor by Symbol</h2>
                <MarketSkewMarketFactorSymbol/>
            </div>
        );
    }
}

export default Market;