import React, { useState, useEffect } from 'react';
import axios from "axios";

import State from './State'

class ErrorReset extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            await axios.post(`/monkey/reset/error`);
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <div>
                <form name="error_reset" onSubmit={this.handleSubmit}>
                    <input data-transaction-name="ErrorReset" type="submit" value="Submit" />
                </form>
                <State key='error_reset' />
            </div>
        );
    }
}

export default ErrorReset;