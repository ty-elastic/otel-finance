import React, { useState, useEffect } from 'react';
import axios from "axios";

class TradeForce extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            symbol: 'MOT',
            dayOfWeek: 'M',
            customerId: "tb93",
            region: 'NA',
            shares: 93,
            sharePrice: 107.10,
            action: 'buy'
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
            await axios.post("/trader/trade/force", null, {
                params: {
                    'symbol': this.state.symbol,
                    'day_of_week': this.state.dayOfWeek,
                    'customer_id': this.state.customerId,
                    'region': this.state.region,
                    'action': this.state.action,
                    'shares': this.state.shares,
                    'share_price': this.state.sharePrice,

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
                <br />
                <label>
                    Shares:
                    <input type="number" name="shares" value={this.state.shares} min="0" max="10000" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Share Price:
                    <input type="number" step="0.01" name="sharePrice" value={this.state.sharePrice} min="0" max="1000" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Action:
                    <select name="action" value={this.state.action} onChange={this.handleInputChange}>
                        <option value="buy">Buy</option>
                        <option value="sell">Sell</option>
                        <option value="hold">Hold</option>
                    </select>
                </label>
                <br />
                <input type="submit" value="Submit" />
            </form>
        );
    }
}

export default TradeForce;