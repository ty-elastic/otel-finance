import React, { useState, useEffect } from 'react';
import axios from "axios";

import State from './State'

class MarketReset extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            await axios.post(`/monkey/reset/market`);
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="market_reset" onSubmit={this.handleSubmit}>
                    <input data-transaction-name="MarketReset" type="submit" value="Submit" />
                </form>
                <State key='market_reset' />
            </div>
        );
    }
}

export default MarketReset;