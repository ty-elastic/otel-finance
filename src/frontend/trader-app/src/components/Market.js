import React, { useState, useEffect } from 'react';
import axios from "axios";

import MarketTputRegion from './MarketTputRegion'
import MarketTputSymbol from './MarketTputSymbol'
import MarketTputCustomer from './MarketTputCustomer'
import MarketReset from './MarketReset'
import MarketSkewMarketFactorSymbol from './MarketSkewMarketFactorSymbol'

class Market extends React.Component {
    render() {
        return (
            <div>
                <h1>Manipulate Market</h1>

                <h2>Reset Conditions</h2>
                <MarketReset></MarketReset>
                <hr></hr>
                
                <h2>Throughput by Region</h2>
                <MarketTputRegion/>
                <hr></hr>
                <h2>Throughput by Symbol</h2>
                <MarketTputSymbol/>
                <hr></hr>
                <h2>Throughput by Customer</h2>
                <MarketTputCustomer/>
                <hr></hr>

                <h2>Skew Market Factor by Symbol</h2>
                <MarketSkewMarketFactorSymbol/>
            </div>
        );
    }
}

export default Market;