import React, { useState, useEffect } from 'react';
import axios from "axios";

class TestReset extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            await axios.post(`/monkey/reset/test`);
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="test_reset" onSubmit={this.handleSubmit}>
                    <input data-transaction-name="TestReset" type="submit" value="Submit" />
                </form>
            </div>
        );
    }
}

export default TestReset;