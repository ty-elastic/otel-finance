import React, { useState, useEffect } from 'react';
import axios from "axios";

class Train extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dayOfWeek: '',
            region: '',
            symbol: '',
            action: '',
            shares_min: -1,
            shares_max: -1,
            share_price_min: -1,
            share_price_max: -1,
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
            let params = {}

            if (this.state.dayOfWeek !== '') {
                params.day_of_week = this.state.dayOfWeek
            }
            if (this.state.region !== '') {
                params.region = this.state.region
            }
            if (this.state.symbol !== '') {
                params.symbol = this.state.symbol
            }
            if (this.state.action !== '') {
                params.action = this.state.action
            }
            if (this.state.shares_min !== -1) {
                params.shares_min = this.state.shares_min
            }
            if (this.state.shares_max !== -1) {
                params.shares_max = this.state.shares_max
            }
            if (this.state.share_price_min !== -1) {
                params.share_price_min = this.state.share_price_min
            }
            if (this.state.share_price_max !== -1) {
                params.share_price_max = this.state.share_price_max
            }

            await axios.post(`/monkey/train/${this.state.classification}`, null, {
                params: params
            });
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <h1>Train Model</h1>

                <form onSubmit={this.handleSubmit}>
                    <label>
                        Day of week:
                        <select name="dayOfWeek"
                            value={this.state.dayOfWeek}
                            displayEmpty
                            onChange={this.handleInputChange}>
                            <option value="">None</option>
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
                        <select name="region"
                            value={this.state.region}
                            displayEmpty
                            onChange={this.handleInputChange}>
                            <option value="">None</option>
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
                        <select name="action"
                            value={this.state.action}
                            displayEmpty
                            onChange={this.handleInputChange}>
                            <option value="">None</option>
                            <option value="buy">Buy</option>
                            <option value="sell">Sell</option>
                            <option value="hold">Hold</option>
                        </select>
                    </label>
                    <br />

                    <label>
                        Shares (Min):
                        <input type="number" name="shares_min" value={this.state.shares_min} min="-1" max="1000" onChange={this.handleInputChange} />
                    </label>
                    <br />
                    <label>
                        Shares (Max):
                        <input type="number" name="shares_max" value={this.state.shares_max} min="-1" max="1000" onChange={this.handleInputChange} />
                    </label>
                    <br />
                    <label>
                        Share Price (Min):
                        <input type="number" name="share_price_min" value={this.state.share_price_min} min="-1" max="100" onChange={this.handleInputChange} />
                    </label>
                    <br />
                    <label>
                        Share Price (Max):
                        <input type="number" name="share_price_max" value={this.state.share_price_max} min="-1" max="100" onChange={this.handleInputChange} />
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
            </div>
        );
    }
}

export default Train;