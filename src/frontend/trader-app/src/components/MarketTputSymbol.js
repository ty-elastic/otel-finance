import React, { useState, useEffect } from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState'

class MarketTputSymbol extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tput_symbol_speed: 'default',
            tput_symbol: 'MOT'
        };

        this.monkeyState = new MonkeyState(this, 'high_tput_per_symbol');

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

            if (this.state.tput_symbol_speed === 'default') {
                await axios.delete(`/monkey/tput/symbol/${this.state.tput_symbol}`);
            } else {
                await axios.post(`/monkey/tput/symbol/${this.state.tput_symbol}/${this.state.tput_symbol_speed}`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="tput_symbol" onSubmit={this.handleSubmit}>
                    <label>
                        Speed:
                        <select name="tput_symbol_speed" value={this.state.tput_symbol_speed} onChange={this.handleInputChange}>
                            <option value="high">High</option>
                            <option value="default">Default</option>
                        </select>
                    </label>
                    <br />
                    <label>
                        Symbol:
                        <select name="tput_symbol" value={this.state.tput_symbol} onChange={this.handleInputChange}>
                            <option value="MOT">MOT</option>
                            <option value="MSI">MSI</option>
                            <option value="GOGO">GOGO</option>
                            <option value="INTEQ">INTEQ</option>
                            <option value="VID">VID</option>
                            <option value="ESTC">ESTC</option>
                        </select>
                    </label>
                    <br />
                    <input data-transaction-name="MarketTputSymbol" type="submit" value="Submit" />
                </form>
                {this.monkeyState.render()}
            </div>
        );
    }
}

export default MarketTputSymbol;