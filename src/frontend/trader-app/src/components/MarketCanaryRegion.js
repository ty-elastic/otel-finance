import React, { useState, useEffect } from 'react';
import axios from "axios";

import State from './State'

class MarketCanaryRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            canary_region_on: false,
            canary_region: 'EU'
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
            if (this.state.canary_region_on === false) {
                await axios.delete(`/monkey/canary/region/${this.state.canary_region}`);
            } else {
                await axios.post(`/monkey/canary/region/${this.state.canary_region}`);
            }
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="canary_region" onSubmit={this.handleSubmit}>
                    <label>
                        Canary:
                        <input type="checkbox" name="canary_region_on" value={this.state.canary_region_on} onChange={this.handleInputChange}/>
                    </label>
                    <br />
                    <label>
                        Region:
                        <select name="canary_region" value={this.state.canary_region} onChange={this.handleInputChange}>
                            <option value="EMEA">EMEA</option>
                            <option value="EU">EU</option>
                            <option value="LATAM">LATAM</option>
                            <option value="NA">NA</option>
                        </select>
                    </label>
                    <br />
                    <input type="submit" value="Submit" />
                </form>
                <State key='canary_per_region'/>
            </div>
        );
    }
}

export default MarketCanaryRegion;