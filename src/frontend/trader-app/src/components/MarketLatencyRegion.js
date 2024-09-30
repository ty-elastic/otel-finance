import React, { useState, useEffect } from 'react';
import axios from "axios";

import State from './State'

class MarketLatencyRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            latency_region_amount: 0,
            latency_region: 'NA',
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
            if (this.state.latency_region_amount === 0) {
                await axios.delete(`/monkey/latency/region/${this.state.latency_region}`);
            } else {
                await axios.post(`/monkey/latency/region/${this.state.latency_region}/${this.state.latency_region_amount}`);
            }
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
                    <input type="submit" value="Submit" /> 
                </form>
                <State key={'latency_per_region'} />
            </div>
        );
    }
}

export default MarketLatencyRegion;