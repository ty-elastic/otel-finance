import React, { useState, useEffect } from 'react';
import axios from "axios";

class MarketTputCustomer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tput_customer_speed: 'default',
            tput_customer: 'q.bert'
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
            if (this.state.tput_customer_speed === 'default') {
                await axios.delete(`/monkey/tput/customer/${this.state.tput_customer}`);
            } else {
                await axios.post(`/monkey/tput/customer/${this.state.tput_customer}/${this.state.tput_customer_speed}`);
            }
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="tput_region" onSubmit={this.handleSubmit}>
                <label>
                    Speed:
                    <select name="tput_customer_speed" value={this.state.tput_customer_speed} onChange={this.handleInputChange}>
                        <option value="high">High</option>
                        <option value="default">Default</option>
                    </select>
                </label>
                <br />
                <label>
                    Customer:
                    <select name="tput_customer" value={this.state.tput_customer} onChange={this.handleInputChange}>
                        <option value="b.smith">b.smith</option>
                        <option value="l.johnson">l.johnson</option>
                        <option value="j.casey">j.casey</option>
                        <option value="l.hall">l.hall</option>
                        <option value="q.bert">q.bert</option>
                    </select>
                </label>
                <br />
                <input type="submit" value="Submit" />
            </form>
        );
    }
}

export default MarketTputCustomer;