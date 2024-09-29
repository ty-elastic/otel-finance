import React, { useState, useEffect } from 'react';
import axios from "axios";

class Trader extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            symbol: 'MOT',
            dayOfWeek: 'M',
            customerId: "tb93",
            region: 'NA'
        };

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
            await axios.post("/trader/trade", null, {
                params: {
                    'symbol': this.state.symbol,
                    'day_of_week': this.state.dayOfWeek,
                    'customer_id': this.state.customerId,
                    //'latency': this.state.latency,
                    'region': this.state.region,
                    //'error_model': this.state.errorModel,
                    //'error_db': this.state.errorDb,
                    //'skew_market_factor': this.state.skewMarketFactor,
                    //'canary': this.state.canary,
                }
            });
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <label>
                    Symbol:
                    <input
                        name="symbol"
                        type="text"
                        value={this.state.symbol}
                        onChange={this.handleInputChange} />
                </label>
                <br />
                <label>
                    Day of week:
                    <select name="dayOfWeek" value={this.state.dayOfWeek} onChange={this.handleInputChange}>
                        <option value="M">Monday</option>
                        <option value="Tu">Tuesday</option>
                        <option value="W">Wednesday</option>
                        <option value="Th">Thursday</option>
                        <option value="F">Friday</option>
                    </select>
                </label>
                <br />
                <label>
                    Customer ID:
                    <input
                        name="customerId"
                        type="text"
                        value={this.state.customerId}
                        onChange={this.handleInputChange} />
                </label>
                <br />
                <label>
                    Region:
                    <select name="region" value={this.state.region} onChange={this.handleInputChange}>
                        <option value="EMEA">EMEA</option>
                        <option value="EU">EU</option>
                        <option value="LATAM">LATAM</option>
                        <option value="NA">NA</option>
                    </select>
                </label>
                <input type="submit" value="Submit" />
            </form>
        );
    }
}

export default Trader;