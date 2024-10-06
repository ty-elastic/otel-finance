import React, { useState, useEffect } from 'react';
import axios from "axios";

class Train extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dayOfWeek: null,
            region: null,
            symbol: null,
            action: null,
            shares_min: 93,
            shares_max: 107,
            share_price_min: 10,
            share_price_max: 100,
            classification: 'fraud'
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
            await axios.post(`/monkey/train/${this.state.classification}`, null, {
                params: {
                    'day_of_week': this.state.dayOfWeek,
                    'region': this.state.region,
                    'symbol': this.state.symbol,
                    'action': this.state.action,
                    'shares_min': this.state.shares_min,
                    'shares_max': this.state.shares_max,
                    'share_price_min': this.state.share_price_min,
                    'share_price_max': this.state.share_price_max
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
                    Symbol:
                    <input
                        name="symbol"
                        type="text"
                        value={this.state.symbol}
                        onChange={this.handleInputChange} />
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

                <label>
                    Shares (Min):
                    <input type="number" name="shares_min" value={this.state.shares_min} min="0" max="1000" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Shares (Max):
                    <input type="number" name="shares_max" value={this.state.shares_max} min="0" max="1000" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Share Price (Min):
                    <input type="number" name="share_price_min" value={this.state.share_price_min} min="0" max="100" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Share Price (Max):
                    <input type="number" name="share_price_max" value={this.state.share_price_max} min="0" max="100" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Classification:
                    <input
                        name="classification"
                        type="text"
                        value={this.state.classification}
                        onChange={this.handleInputChange} />
                </label>

                <input data-transaction-name="Train" type="submit" value="Submit" />
            </form>
        );
    }
}

export default Train;