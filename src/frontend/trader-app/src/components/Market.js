import React, { useState, useEffect } from 'react';
import axios from "axios";

import MarketTputRegion from './MarketTputRegion'
import MarketTputSymbol from './MarketTputSymbol'
import MarketTputCustomer from './MarketTputCustomer'
import MarketReset from './MarketReset'
import MarketSkewMarketFactorSymbol from './MarketSkewMarketFactorSymbol'

import Page from './Page'

const sections = [
    { label: 'Reset', desc: 'Reset market conditions', element: MarketReset },
    { label: 'Throughput by Region', desc: 'High throughput by region', element: MarketTputRegion },
    { label: 'Throughput by Symbol', desc: 'High throughput by symbol', element: MarketTputSymbol },
    { label: 'Throughput by Customer', desc: 'High throughput by customer', element: MarketTputCustomer },
    { label: 'Skew Market Factor', desc: 'Skew market factor by symbol', element: MarketSkewMarketFactorSymbol }
];

class Market extends React.Component {
    render() {
        return (
            <Page sections={sections}></Page>
        );
    }
}

export default Market;