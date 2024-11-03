import React, { useState, useEffect } from 'react';
import axios from "axios";

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
            </div>
        );
    }
}

export default MarketReset;