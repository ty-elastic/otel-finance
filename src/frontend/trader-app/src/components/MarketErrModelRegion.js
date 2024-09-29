import React, { useState, useEffect } from 'react';
import axios from "axios";

class MarketErrModelRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            err_model_region_amount: 0,
            err_model_region: 'EU',
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
            if (this.state.err_model_region_amount === 0) {
                await axios.delete(`/monkey/err/model/region/${this.state.err_model_region}`);
            } else {
                await axios.post(`/monkey/err/model/region/${this.state.err_model_region}/${this.state.err_model_region_amount}`);
            }
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="err_model_region" onSubmit={this.handleSubmit}>
                <label>
                    Amount (%):
                    <input type="number" name="err_model_region_amount" value={this.state.err_model_region_amount} min="0" max="100" onChange={this.handleInputChange}/>
                </label>
                <br />
                <label>
                    Region:
                    <select name="latency_region" value={this.state.err_model_region} onChange={this.handleInputChange}>
                        <option value="EMEA">EMEA</option>
                        <option value="EU">EU</option>
                        <option value="LATAM">LATAM</option>
                        <option value="NA">NA</option>
                    </select>
                </label>
                <br />
                <input type="submit" value="Submit" />
            </form>
        );
    }
}

export default MarketErrModelRegion;