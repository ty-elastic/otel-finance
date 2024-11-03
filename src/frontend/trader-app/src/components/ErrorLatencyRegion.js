import React, { useState, useEffect } from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState';

class ErrorLatencyRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            latency_region_amount: 0,
            latency_region: 'NA',
            latency_region_action: 'Any'
        };

        this.monkeyState = new MonkeyState(this, 'latency_per_action_per_region');

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
            if (this.state.latency_region_amount === 0) {
                await axios.delete(`/monkey/latency/region/${this.state.latency_region}`);
            } else {
                await axios.post(`/monkey/latency/region/${this.state.latency_region}/${this.state.latency_region_amount}`,
                    null,
                    {
                        params: {
                            'latency_action': (this.state.latency_action === 'any')?null:this.state.latency_action
                        }
                    }
                );
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="latency_region" onSubmit={this.handleSubmit}>
                    <label>
                        Amount (ms):
                        <input type="number" name="latency_region_amount" value={this.state.latency_region_amount} min="0" max="2000" onChange={this.handleInputChange} />
                    </label>
                    <br />
                    <label>
                        Region:
                        <select name="latency_region" value={this.state.latency_region} onChange={this.handleInputChange}>
                            <option value="EMEA">EMEA</option>
                            <option value="EU">EU</option>
                            <option value="LATAM">LATAM</option>
                            <option value="NA">NA</option>
                        </select>
                    </label>
                    <br />
                    <label>
                        Action:
                        <select name="latency_action" value={this.state.latency_action} onChange={this.handleInputChange}>
                            <option value="any">Any</option>
                            <option value="buy">Buy</option>
                            <option value="sell">Sell</option>
                            <option value="hold">Hold</option>
                        </select>
                    </label>
                    <br />
                    <input data-transaction-name="ErrorLatencyRegion" type="submit" value="Submit" /> 
                </form>
                {this.monkeyState.render()}
            </div>
        );
    }
}

export default ErrorLatencyRegion;