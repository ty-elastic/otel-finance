import React, { useState, useEffect } from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState'

class MarketSkewMarketFactorSymbol extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            skew_market_factor_symbol_amount: 0,
            skew_market_factor_symbol: 'MOT',
        };

        this.monkeyState = new MonkeyState(this, 'skew_market_factor_per_symbol');

        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            if (this.state.skew_market_factor_symbol_amount === 0) {
                await axios.delete(`/monkey/skew_market_factor/symbol/${this.state.skew_market_factor_symbol}`);
            } else {
                await axios.post(`/monkey/skew_market_factor/symbol/${this.state.skew_market_factor_symbol}/${this.state.skew_market_factor_symbol_amount}`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="skew_market_factor_symbol" onSubmit={this.handleSubmit}>
                    <label>
                        Amount:
                        <input type="number" name="skew_market_factor_symbol_amount" value={this.state.skew_market_factor_symbol_amount} min="-100" max="100" onChange={this.handleInputChange} />
                    </label>
                    <br />
                    <label>
                        Symbol:
                        <select name="skew_market_factor_symbol" value={this.state.skew_market_factor_symbol} onChange={this.handleInputChange}>
                            <option value="MOT">MOT</option>
                            <option value="MSI">MSI</option>
                            <option value="GOGO">GOGO</option>
                            <option value="INTEQ">INTEQ</option>
                            <option value="VID">VID</option>
                            <option value="ESTC">ESTC</option>
                        </select>
                    </label>
                    <br />
                    <input data-transaction-name="MarketSkewMarketFactorSymbol" type="submit" value="Submit" />
                </form>
                {this.monkeyState.render()}
            </div>
        );
    }
}

export default MarketSkewMarketFactorSymbol;