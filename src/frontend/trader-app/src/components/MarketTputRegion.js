import React, { useState, useEffect } from 'react';
import axios from "axios";

import State from './State'

class MarketTputRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tput_region_speed: 'default',
            tput_region: 'NA',
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
            if (this.state.tput_region_speed === 'default') {
                await axios.delete(`/monkey/tput/region/${this.state.tput_region}`);
            } else {
                await axios.post(`/monkey/tput/region/${this.state.tput_region}/${this.state.tput_region_speed}`);
            }
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="tput_region" onSubmit={this.handleSubmit}>
                    <label>
                        Speed:
                        <select name="tput_region_speed" value={this.state.tput_region_speed} onChange={this.handleInputChange}>
                            <option value="high">High</option>
                            <option value="default">Default</option>
                        </select>
                    </label>
                    <br />
                    <label>
                        Region:
                        <select name="tput_region" value={this.state.tput_region} onChange={this.handleInputChange}>
                            <option value="EMEA">EMEA</option>
                            <option value="EU">EU</option>
                            <option value="LATAM">LATAM</option>
                            <option value="NA">NA</option>
                        </select>
                    </label>
                    <br />
                    <input type="submit" value="Submit" />
                </form>
                <State key='high_tput_per_region' />
            </div>
        );
    }
}

export default MarketTputRegion;